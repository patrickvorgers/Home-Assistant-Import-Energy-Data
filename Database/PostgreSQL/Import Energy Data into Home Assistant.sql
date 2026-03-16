-- PostgreSQL: Import Energy data into Home Assistant

/*
IMPORTANT: Before running this script, you need to find the correct sensor IDs from your statistics_meta table.
Run this query to find your sensor metadata IDs:

SELECT id, statistic_id, source, unit_of_measurement 
FROM statistics_meta 
WHERE has_sum = true 
ORDER BY id;

Then update the sensor_id values in the INSERT INTO temp_sensors statements below to match your actual sensor IDs.
Comment out any sensors you don't want to use.
*/

-- Start transaction
BEGIN;

-- Create a temp table for sensor metadata
DROP TABLE IF EXISTS temp_sensors;
CREATE TEMP TABLE temp_sensors (
    name VARCHAR(255) PRIMARY KEY,
    sensor_id INTEGER,
    correction DOUBLE PRECISION,
    cutoff_new_meter DOUBLE PRECISION,
    cutoff_invalid_value DOUBLE PRECISION
);

-- Insert sensor definitions
-- Correction factor: kWh -> kWh = 1.0 (change to 1000.0 if your data is in Wh)
-- COMMENT OUT sensors you don't have by adding -- at the start of the line
INSERT INTO temp_sensors VALUES 
('elec_feed_in_tariff_1',  3,        1.0,       25.0,            1000.0),
('elec_feed_in_tariff_2',  4,        1.0,       25.0,            1000.0),
('elec_feed_out_tariff_1', 5,        1.0,       25.0,            1000.0),
('elec_feed_out_tariff_2', 6,        1.0,       25.0,            1000.0);
-- ('gas',                    7,        1.0,       25.0,            1000.0),
-- ('elec_solar',             8,        1.0,       25.0,            1000.0),
-- ('elec_battery_feed_in',   9,        1.0,       25.0,            1000.0),
-- ('elec_battery_feed_out',  10,       1.0,       25.0,            1000.0),
-- ('water',                  11,       1.0,       25.0,            1000.0);

-- Create a temp table for calculated statistics
DROP TABLE IF EXISTS temp_stats_new;
CREATE TEMP TABLE temp_stats_new (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER NOT NULL,
    ts DOUBLE PRECISION NOT NULL,
    begin_state DOUBLE PRECISION,
    end_state DOUBLE PRECISION,
    diff DOUBLE PRECISION,
    old_sum DOUBLE PRECISION,
    new_sum DOUBLE PRECISION
);

CREATE UNIQUE INDEX idx_sensor_id_ts ON temp_stats_new(sensor_id, ts);

-- Insert high resolution import data
-- Invert sign for feed_out sensors only if value is negative
-- DISTINCT ON removes duplicates, keeping the last occurrence
INSERT INTO temp_stats_new(sensor_id, ts, begin_state)
SELECT DISTINCT ON (s.sensor_id, ROUND(imd.timestamp))
       s.sensor_id, ROUND(imd.timestamp), 
       ROUND((
           CASE 
               WHEN imd.id LIKE '%feed_out%' AND imd.value < 0 THEN -(imd.value / s.correction)
               ELSE imd.value / s.correction
           END
       )::NUMERIC, 3)
FROM import_data imd
JOIN temp_sensors s ON s.name = imd.id
WHERE imd.resolution = 'HIGH'
ORDER BY s.sensor_id, ROUND(imd.timestamp), imd.value DESC;

-- Insert low resolution import data (only older than high res)
-- Invert sign for feed_out sensors only if value is negative
-- DISTINCT ON removes duplicates, keeping the last occurrence
INSERT INTO temp_stats_new(sensor_id, ts, begin_state)
SELECT DISTINCT ON (s.sensor_id, ROUND(imd.timestamp))
       s.sensor_id, ROUND(imd.timestamp), 
       ROUND((
           CASE 
               WHEN imd.id LIKE '%feed_out%' AND imd.value < 0 THEN -(imd.value / s.correction)
               ELSE imd.value / s.correction
           END
       )::NUMERIC, 3)
FROM import_data imd
JOIN temp_sensors s ON s.name = imd.id
LEFT JOIN (
    SELECT sensor_id, MIN(ts) AS min_ts
    FROM temp_stats_new
    GROUP BY sensor_id
) m ON m.sensor_id = s.sensor_id
WHERE imd.resolution = 'LOW' AND imd.timestamp < COALESCE(m.min_ts, EXTRACT(EPOCH FROM NOW()))
ORDER BY s.sensor_id, ROUND(imd.timestamp), imd.value DESC
ON CONFLICT (sensor_id, ts) DO NOTHING;

-- Set end_state using LEAD()
UPDATE temp_stats_new t
SET end_state = n.value
FROM (
    SELECT sensor_id, ts, LEAD(begin_state) OVER(PARTITION BY sensor_id ORDER BY ts) AS value
    FROM temp_stats_new
) n
WHERE t.sensor_id = n.sensor_id AND t.ts = n.ts;

-- Remove overlapping records already in statistics
-- COMMENTED OUT: This prevents overwriting existing data. Uncomment to preserve existing HA data.
/*
DELETE FROM temp_stats_new t
USING (
    SELECT metadata_id, MIN(start_ts) AS min_ts
    FROM statistics
    WHERE metadata_id IN (SELECT sensor_id FROM temp_sensors)
    GROUP BY metadata_id
) s
WHERE t.sensor_id = s.metadata_id AND t.ts >= s.min_ts;
*/

-- Insert existing Home Assistant data
INSERT INTO temp_stats_new(sensor_id, ts, end_state, old_sum)
SELECT metadata_id, start_ts, state, sum
FROM statistics
WHERE metadata_id IN (SELECT sensor_id FROM temp_sensors)
ON CONFLICT (sensor_id, ts) DO UPDATE
SET end_state = EXCLUDED.end_state, old_sum = EXCLUDED.old_sum;

-- Calculate diff for imported and HA data
UPDATE temp_stats_new SET diff = end_state - begin_state WHERE old_sum IS NULL;

WITH diff_calc AS (
    SELECT sensor_id, ts, old_sum - LAG(old_sum) OVER(PARTITION BY sensor_id ORDER BY ts) AS diff
    FROM temp_stats_new
)
UPDATE temp_stats_new t
SET diff = d.diff
FROM diff_calc d
WHERE t.sensor_id = d.sensor_id AND t.ts = d.ts AND t.old_sum IS NOT NULL;

-- Cleanup wrong values
UPDATE temp_stats_new
SET diff = old_sum
WHERE diff IS NULL;

UPDATE temp_stats_new
SET diff = ROUND(end_state::NUMERIC, 3)
WHERE diff < 0 AND end_state < (
    SELECT cutoff_new_meter FROM temp_sensors WHERE temp_stats_new.sensor_id = temp_sensors.sensor_id LIMIT 1
);

UPDATE temp_stats_new
SET diff = 0
WHERE diff < 0 OR diff > (
    SELECT cutoff_invalid_value FROM temp_sensors WHERE temp_stats_new.sensor_id = temp_sensors.sensor_id LIMIT 1
);

-- Calculate new_sum
WITH sum_calc AS (
    SELECT id, SUM(diff) OVER(PARTITION BY sensor_id ORDER BY ts) AS new_sum
    FROM temp_stats_new
)
UPDATE temp_stats_new t
SET new_sum = ROUND(s.new_sum::NUMERIC, 3)
FROM sum_calc s
WHERE t.id = s.id;

-- Backup statistics tables
DROP TABLE IF EXISTS backup_statistics;
CREATE TABLE backup_statistics (id INTEGER PRIMARY KEY, metadata_id INTEGER, sum DOUBLE PRECISION);
CREATE INDEX idx_statistics_metadata_id ON backup_statistics (metadata_id);

INSERT INTO backup_statistics
SELECT id, metadata_id, sum FROM statistics
WHERE metadata_id IN (SELECT sensor_id FROM temp_sensors);

DROP TABLE IF EXISTS backup_statistics_short_term;
CREATE TABLE backup_statistics_short_term (id INTEGER PRIMARY KEY, metadata_id INTEGER, sum DOUBLE PRECISION);
CREATE INDEX idx_statistics_short_term_metadata_id ON backup_statistics_short_term (metadata_id);

INSERT INTO backup_statistics_short_term
SELECT id, metadata_id, sum FROM statistics_short_term
WHERE metadata_id IN (SELECT sensor_id FROM temp_sensors);

-- Insert/update statistics
INSERT INTO statistics(state, sum, metadata_id, created_ts, start_ts)
SELECT end_state, new_sum, sensor_id, ts, ts FROM temp_stats_new
ON CONFLICT (metadata_id, start_ts) DO UPDATE
SET sum = EXCLUDED.sum;

-- Update short-term statistics
WITH correction AS (
    SELECT SST.metadata_id,
           FIRST_VALUE(SN.new_sum - SST.sum) OVER(PARTITION BY SST.metadata_id ORDER BY SST.start_ts DESC) AS correction_factor
    FROM statistics_short_term SST
    JOIN temp_stats_new SN ON SST.metadata_id = SN.sensor_id AND SST.start_ts = SN.ts
)
UPDATE statistics_short_term SST
SET sum = sum + c.correction_factor
FROM correction c
WHERE SST.metadata_id = c.metadata_id;

-- Drop temporary tables
DROP TABLE IF EXISTS temp_sensors;
DROP TABLE IF EXISTS temp_stats_new;
DROP TABLE IF EXISTS import_data;

-- Do not drop the backup tables. They can be deleted after verification by the user.

-- Commit transaction
COMMIT;

