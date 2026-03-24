/* PostgreSQL: Import Energy data into Home Assistant */


/* Start a transaction so that we can rollback any changes if needed */
BEGIN;

/* Create a temp table to hold the used sensor metadata */
DROP TABLE IF EXISTS sensors;
CREATE TEMP TABLE sensors (
    name VARCHAR(255) PRIMARY KEY,
    sensor_id INTEGER NOT NULL,
    correction FLOAT NOT NULL,
    cutoff_new_meter FLOAT NOT NULL,
    cutoff_invalid_value FLOAT NOT NULL
);

/*
Definition of the different sensors for which the history data should be loaded.
Comment out the sensors for which no history data is available.

SENSOR NAME:
  Sensor identifier as specified by the imported data (CSV filename)
SENSOR ID:
  Identifier (id) of the sensor as defined in the statistics_meta table
CORRECTION FACTOR:
  Correction factor in case the provided data uses a different unit of measurement than the target sensor (import data -> target sensor)
    Wh  -> Wh  : 1.0
    Wh  -> kWh : 1000.0
    Wh  -> MWh : 1000000.0
    kWh -> Wh  : 0.001
    kWh -> kWh : 1.0
    kWh -> MWh : 0.001
    MWh -> Wh  : 0.000001
    MWh -> kWh : 0.001
    MWh -> MWh : 1.0
    L   -> L   : 1.0
    L   -> m³  : 1000
    m³  -> L   : 0.001
    m³  -> m³  : 1.0
CUTOFF NEW METER:
  This value determines the cutoff value to determine when a new meter is installed. The value depends on the unit of measurement of the target sensor!
  Change this in case your new meter started with a higher start value.
  New meter detection: (difference between two sensor states < 0) and (state of sensor < cutoff new meter value)
    Wh  : 25000.0 Wh
    kWh : 25.0 kWh
    MWh : 0.025 MWh
    L   : 25000.0 L
    m³  : 25.0 m³
CUTOFF INVALID VALUE:
  This value determines when a value is considered to be invalid (too large). The value depends on the unit of measurement of the target sensor!
  For instance, this can occur when the imported data is recalculated (since the import shows usage per interval rather than actual readings).
  This may produce a large spike at the point where the imported data transitions to the Home Assistant data.
  Change this in case a higher/lower diff cutoff is needed to mark a value invalid.
  Invalid value detection: (difference between two sensor states > cutoff invalid value)
    Wh  : 1000000.0 Wh
    kWh : 1000.0 kWh
    MWh : 1 MWh
    L   : 1000000.0 L
    m³  : 1000.0 m³

Examples:
Wh -> Wh (import data is in Wh and target sensor data is in Wh)
correction cutoff_new_meter cutoff_invalid_value
1.0        25000.0          1000000.0

Wh -> kWh (import data is in Wh and target sensor data is in kWh)
correction cutoff_new_meter cutoff_invalid_value
1000.0     25.0             1000.0

Wh -> MWh (import data is in Wh and target sensor data is in MWh)
correction cutoff_new_meter cutoff_invalid_value
1000000.0  0.025            1.0

L -> m³ (import data is in L and target sensor data is in m³)
correction cutoff_new_meter cutoff_invalid_value
1000.0     25.0             1000.0
*/

/*                          name                      sensor_id correction cutoff_new_meter cutoff_invalid_value */
INSERT INTO sensors VALUES ('gas',                    6,        1000.0,    25.0,            1000.0); /* Change */
INSERT INTO sensors VALUES ('elec_feed_in_tariff_1',  7,        1000.0,    25.0,            1000.0); /* Change */
INSERT INTO sensors VALUES ('elec_feed_in_tariff_2',  8,        1000.0,    25.0,            1000.0); /* Change */
INSERT INTO sensors VALUES ('elec_feed_out_tariff_1', 9,        1000.0,    25.0,            1000.0); /* Change */
INSERT INTO sensors VALUES ('elec_feed_out_tariff_2', 10,       1000.0,    25.0,            1000.0); /* Change */
INSERT INTO sensors VALUES ('elec_solar',             352,      1000.0,    25.0,            1000.0); /* Change */
INSERT INTO sensors VALUES ('elec_battery_feed_in',   450,      1000.0,    25.0,            1000.0); /* Change */
INSERT INTO sensors VALUES ('elec_battery_feed_out',  451,      1000.0,    25.0,            1000.0); /* Change */
INSERT INTO sensors VALUES ('water',                  653,      1000.0,    25.0,            1000.0); /* Change */

/* FOR NORMAL USAGE THERE SHOULD BE NO CHANGES NEEDED AFTER THIS POINT */


/* Create a temp table that can hold the difference between the measurements and create a new sum */
DROP TABLE IF EXISTS stats_new;
CREATE TEMP TABLE stats_new (
  id            SERIAL PRIMARY KEY,
  sensor_id     INTEGER NOT NULL,
  ts            DOUBLE PRECISION NOT NULL,
  begin_state   DOUBLE PRECISION,
  end_state     DOUBLE PRECISION,
  diff          DOUBLE PRECISION,
  old_sum       DOUBLE PRECISION,
  new_sum       DOUBLE PRECISION
);
CREATE UNIQUE INDEX idx_sensor_id_ts ON stats_new (sensor_id, ts);


/* Insert the high resolution records and apply the correction

   The values are the start of the interval
*/
INSERT INTO stats_new (sensor_id, ts, begin_state)
SELECT s.sensor_id, ROUND(imd.timestamp::NUMERIC, 0)::DOUBLE PRECISION, ROUND((imd.value / s.correction)::NUMERIC, 3)::DOUBLE PRECISION
FROM import_data AS imd
JOIN sensors AS s ON s.name = imd.id
WHERE
  imd.resolution = 'HIGH';


/* Insert the low resolution records and apply the correction.
   We only add data that is older than the high resolution records

   The values are the start of the interval
*/
INSERT INTO stats_new (sensor_id, ts, begin_state)
SELECT s.sensor_id, ROUND(imd.timestamp::NUMERIC, 0)::DOUBLE PRECISION, ROUND((imd.value / s.correction)::NUMERIC, 3)::DOUBLE PRECISION
FROM import_data AS imd
JOIN sensors AS s ON s.name = imd.id
LEFT JOIN (
  SELECT sensor_id, MIN(ts) AS min_ts
  FROM stats_new
  GROUP BY sensor_id
) AS m ON m.sensor_id = s.sensor_id
WHERE
  imd.resolution = 'LOW' AND
  imd.timestamp < COALESCE(m.min_ts, EXTRACT(EPOCH FROM NOW()));


/* Determine the end of the interval for the imported data */
UPDATE stats_new
SET end_state = NEXT_VALUES.value
FROM (SELECT sensor_id, ts, LEAD(begin_state, 1) OVER (PARTITION BY sensor_id ORDER BY sensor_id, ts) AS value
  FROM stats_new
  ORDER BY sensor_id, ts) AS NEXT_VALUES
WHERE
  stats_new.sensor_id = NEXT_VALUES.sensor_id AND
  stats_new.ts = NEXT_VALUES.ts;


/* Remove any overlapping records from the imported data that are already in Home Assistant */
DELETE FROM stats_new
WHERE (sensor_id, ts) IN (
  SELECT SN.sensor_id, SN.ts
  FROM stats_new SN
  JOIN (
    SELECT metadata_id, MIN(start_ts) AS min_ts
    FROM statistics
    WHERE
      metadata_id IN (SELECT sensor_id FROM sensors)
    GROUP BY metadata_id
  ) SENSOR_MIN_TS ON SN.sensor_id = SENSOR_MIN_TS.metadata_id
  WHERE
    SN.ts >= SENSOR_MIN_TS.min_ts
);


/* Insert the data from Home Assistant so that we can adjust the records with the new calculated sum
   Home Assistant records only have the end state of the interval
*/
INSERT INTO stats_new (sensor_id, ts, end_state, old_sum)
SELECT metadata_id, start_ts, state, sum
FROM statistics
WHERE metadata_id IN (SELECT sensor_id FROM sensors);


/* Calculate the difference per interval
  - For the imported data, calculate the diff by subtracting the begin_state from the end_state (old_sum is NULL)
*/
UPDATE stats_new
SET diff = end_state - begin_state
WHERE
  old_sum IS NULL;

/* Calculate the difference for Home Assistant records using the sum column */
UPDATE stats_new
SET diff = DIFF_STATS_SUM.diff
FROM (SELECT sensor_id, ts, (old_sum - LAG(old_sum, 1) OVER (PARTITION BY sensor_id ORDER BY sensor_id, ts)) AS diff
 FROM stats_new
 ORDER BY sensor_id, ts) AS DIFF_STATS_SUM
WHERE
  stats_new.sensor_id = DIFF_STATS_SUM.sensor_id AND
  stats_new.ts = DIFF_STATS_SUM.ts AND
  stats_new.old_sum IS NOT NULL;


/* Cleanup possible wrong values:
  - Diff is null  => The point where the imported data goes over to Home Assistant data
  - Diff < 0   => Probably new meter installed (measurement should be low)
  - Diff > invalid => Incorrect value
*/
UPDATE stats_new
SET diff = old_sum
WHERE
  diff IS NULL;

UPDATE stats_new
SET diff = ROUND(end_state::NUMERIC, 3)::DOUBLE PRECISION
WHERE
  (diff < 0.0) AND
  (end_state < (SELECT cutoff_new_meter FROM sensors WHERE stats_new.sensor_id = sensors.sensor_id LIMIT 1));

UPDATE stats_new
SET diff = 0
WHERE
  (diff < 0.0) OR
  (diff > (SELECT cutoff_invalid_value FROM sensors WHERE stats_new.sensor_id = sensors.sensor_id LIMIT 1));


/* Calculate the new sum
   It is calculated by calculating the sum up till the record that is currently processed
*/
UPDATE stats_new
SET new_sum = ROUND((SUM_STATS.new_sum)::NUMERIC, 3)::DOUBLE PRECISION
FROM (SELECT sensor_id, ts, SUM(diff) OVER (PARTITION BY sensor_id ORDER BY sensor_id, ts) AS new_sum
 FROM stats_new) AS SUM_STATS
WHERE
  stats_new.sensor_id = SUM_STATS.sensor_id AND
  stats_new.ts = SUM_STATS.ts;


/* Copy records from the original tables into the backup tables
   We only copy the records for the sensors that are defined in sensors
*/
DROP TABLE IF EXISTS backup_statistics;
CREATE TABLE backup_statistics (id BIGINT PRIMARY KEY, metadata_id INTEGER, sum DOUBLE PRECISION);
CREATE INDEX idx_statistics_metadata_id ON backup_statistics (metadata_id);

INSERT INTO backup_statistics
SELECT id, metadata_id, sum FROM statistics
WHERE
  metadata_id IN (SELECT sensor_id FROM sensors);

DROP TABLE IF EXISTS backup_statistics_short_term;
CREATE TABLE backup_statistics_short_term (id BIGINT PRIMARY KEY, metadata_id INTEGER, sum DOUBLE PRECISION);
CREATE INDEX idx_statistics_short_term_metadata_id ON backup_statistics_short_term (metadata_id);

INSERT INTO backup_statistics_short_term
SELECT id, metadata_id, sum FROM statistics_short_term
WHERE
  metadata_id IN (SELECT sensor_id FROM sensors);


/* Copy the new information to the statistics table
id          => primary key and automatically filled (autoincrement)
state       => the end_state of the interval
sum         => calculated new_sum value
metadata_id => the fixed metadata id of this statistics (see top)
created_ts  => set to the timestamp of the statistic
start_ts    => timestamp of the statistic
The sum is updated in case the record is already in Home Assistant
*/
INSERT INTO statistics (state, sum, metadata_id, created_ts, start_ts)
SELECT end_state, new_sum, sensor_id, ts, ts FROM stats_new
ON CONFLICT(metadata_id, start_ts) DO UPDATE SET sum = EXCLUDED.sum;


/* Also update the short term statistics.
   We calculate the delta with which the sum was changed and add that to the current measurements
*/
WITH correction AS (
    SELECT SST.metadata_id,
           FIRST_VALUE(SN.new_sum - SST.sum) OVER(PARTITION BY SST.metadata_id ORDER BY SST.start_ts DESC) AS correction_factor
    FROM statistics_short_term SST
    JOIN stats_new SN ON SST.metadata_id = SN.sensor_id AND SST.start_ts = SN.ts
)
UPDATE statistics_short_term SST
SET sum = sum + c.correction_factor
FROM correction c
WHERE SST.metadata_id = c.metadata_id;


/* Remove the temporary tables */
DROP TABLE IF EXISTS sensors;
DROP TABLE IF EXISTS stats_new;
DROP TABLE IF EXISTS import_data;

/* Do not drop the backup tables. They can be deleted after verification by the user. */

/* Commit the changes - can be commented out while testing */
COMMIT;