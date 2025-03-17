/* SQLite: Import energy/water data into Home Assistant */


/* Create a temp table to hold the used sensor metadata */
DROP TABLE IF EXISTS SENSORS;
CREATE TEMP TABLE SENSORS (name TEXT PRIMARY KEY, sensor_id INTEGER, correction FLOAT, cutoff_new_meter FLOAT, cutoff_invalid_value FLOAT);

/*
Definition of the different sensors for which the history data should be loaded.
Comment out the sensors for which no history data is available.

SENSOR NAME:
  Fixed, do not change this
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

/*                          name                                sensor_id correction cutoff_new_meter cutoff_invalid_value */
INSERT INTO SENSORS VALUES ('sensor_id_gas',                    6,        1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('sensor_id_elec_feed_in_tariff_1',  7,        1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('sensor_id_elec_feed_in_tariff_2',  8,        1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('sensor_id_elec_feed_out_tariff_1', 9,        1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('sensor_id_elec_feed_out_tariff_2', 10,       1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('sensor_id_elec_solar',             352,      1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('sensor_id_elec_battery_feed_in',   450,      1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('sensor_id_elec_battery_feed_out',  451,      1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('sensor_id_water',                  653,      1000.0,    25.0,            1000.0); /* Change */


/* FOR NORMAL USAGE THERE SHOULD BE NO CHANGES NEEDED AFTER THIS POINT */


/* Create empty temp import tables if they do not exist so that the SQL statements do not break in case the table is not imported */
CREATE TABLE IF NOT EXISTS elec_feed_in_tariff_1_high_resolution (field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_in_tariff_1 
CREATE TABLE IF NOT EXISTS elec_feed_in_tariff_1_low_resolution  (field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_in_tariff_1 
CREATE TABLE IF NOT EXISTS elec_feed_in_tariff_2_high_resolution (field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_in_tariff_2
CREATE TABLE IF NOT EXISTS elec_feed_in_tariff_2_low_resolution  (field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_in_tariff_2
CREATE TABLE IF NOT EXISTS elec_feed_out_tariff_1_high_resolution(field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_out_tariff_1
CREATE TABLE IF NOT EXISTS elec_feed_out_tariff_1_low_resolution (field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_out_tariff_1
CREATE TABLE IF NOT EXISTS elec_feed_out_tariff_2_high_resolution(field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_out_tariff_2
CREATE TABLE IF NOT EXISTS elec_feed_out_tariff_2_low_resolution (field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_out_tariff_2
CREATE TABLE IF NOT EXISTS elec_solar_high_resolution            (field1 FLOAT, field2 FLOAT); -- sensor_id_elec_solar
CREATE TABLE IF NOT EXISTS elec_solar_low_resolution             (field1 FLOAT, field2 FLOAT); -- sensor_id_elec_solar
CREATE TABLE IF NOT EXISTS elec_battery_feed_in_high_resolution  (field1 FLOAT, field2 FLOAT); -- sensor_id_elec_battery_feed_in
CREATE TABLE IF NOT EXISTS elec_battery_feed_in_low_resolution   (field1 FLOAT, field2 FLOAT); -- sensor_id_elec_battery_feed_in
CREATE TABLE IF NOT EXISTS elec_battery_feed_out_high_resolution (field1 FLOAT, field2 FLOAT); -- sensor_id_elec_battery_feed_out
CREATE TABLE IF NOT EXISTS elec_battery_feed_out_low_resolution  (field1 FLOAT, field2 FLOAT); -- sensor_id_elec_battery_feed_out
CREATE TABLE IF NOT EXISTS gas_high_resolution                   (field1 FLOAT, field2 FLOAT); -- sensor_id_gas
CREATE TABLE IF NOT EXISTS gas_low_resolution                    (field1 FLOAT, field2 FLOAT); -- sensor_id_gas
CREATE TABLE IF NOT EXISTS water_high_resolution                 (field1 FLOAT, field2 FLOAT); -- sensor_id_water
CREATE TABLE IF NOT EXISTS water_low_resolution                  (field1 FLOAT, field2 FLOAT); -- sensor_id_water

/* Create temp tables that can hold the difference between the measurements and create a new sum */
DROP TABLE IF EXISTS STATS_NEW;
CREATE TEMP TABLE STATS_NEW (
  sensor_id 	INTEGER NOT NULL,
  ts        	FLOAT NOT NULL,
  begin_state	FLOAT,
  end_state		FLOAT,
  diff      	FLOAT,
  old_sum   	FLOAT,
  new_sum   	FLOAT
);
CREATE UNIQUE INDEX idx_sensor_id_ts ON STATS_NEW (sensor_id, ts);

/* Insert the high resolution records and apply the correction 

   Invalid rows with null values are ignored
   The values are the start of the interval
   Grouping by field1 is done to remove any duplicates
*/
WITH CTE_ALL_HIGH_RESOLUTION AS (
  SELECT 'sensor_id_elec_feed_in_tariff_1' AS sensor_name, field1, field2 FROM elec_feed_in_tariff_1_high_resolution
  UNION ALL
  SELECT 'sensor_id_elec_feed_in_tariff_2', field1, field2 FROM elec_feed_in_tariff_2_high_resolution
  UNION ALL
  SELECT 'sensor_id_elec_feed_out_tariff_1', field1, field2 FROM elec_feed_out_tariff_1_high_resolution
  UNION ALL
  SELECT 'sensor_id_elec_feed_out_tariff_2', field1, field2 FROM elec_feed_out_tariff_2_high_resolution
  UNION ALL
  SELECT 'sensor_id_elec_solar', field1, field2 FROM elec_solar_high_resolution
  UNION ALL
  SELECT 'sensor_id_elec_battery_feed_in', field1, field2 FROM elec_battery_feed_in_high_resolution
  UNION ALL
  SELECT 'sensor_id_elec_battery_feed_out', field1, field2 FROM elec_battery_feed_out_high_resolution
  UNION ALL
  SELECT 'sensor_id_gas', field1, field2 FROM gas_high_resolution
  UNION ALL
  SELECT 'sensor_id_water', field1, field2 FROM water_high_resolution
)
INSERT INTO STATS_NEW (sensor_id, ts, begin_state)
SELECT sensor_id, ROUND(field1, 0), ROUND(field2 / correction, 3)
FROM CTE_ALL_HIGH_RESOLUTION
JOIN SENSORS ON name = sensor_name
WHERE (field1 IS NOT NULL) AND (field2 IS NOT NULL)
GROUP BY sensor_name, field1;


/* Insert the low resolution records and apply the correction.
   We only add data that is older than the high resolution records

   Invalid rows with null values are ignored
   The values are the start of the interval
   Grouping by field1 is done to remove any duplicates
*/
WITH CTE_ALL_LOW_RESOLUTION AS (
  SELECT 'sensor_id_elec_feed_in_tariff_1' AS sensor_name, field1, field2 FROM elec_feed_in_tariff_1_low_resolution
  UNION ALL
  SELECT 'sensor_id_elec_feed_in_tariff_2', field1, field2 FROM elec_feed_in_tariff_2_low_resolution
  UNION ALL
  SELECT 'sensor_id_elec_feed_out_tariff_1', field1, field2 FROM elec_feed_out_tariff_1_low_resolution
  UNION ALL
  SELECT 'sensor_id_elec_feed_out_tariff_2', field1, field2 FROM elec_feed_out_tariff_2_low_resolution
  UNION ALL
  SELECT 'sensor_id_elec_solar', field1, field2 FROM elec_solar_low_resolution
  UNION ALL
  SELECT 'sensor_id_elec_battery_feed_in', field1, field2 FROM elec_battery_feed_in_low_resolution
  UNION ALL
  SELECT 'sensor_id_elec_battery_feed_out', field1, field2 FROM elec_battery_feed_out_low_resolution
  UNION ALL
  SELECT 'sensor_id_gas', field1, field2 FROM gas_low_resolution
  UNION ALL
  SELECT 'sensor_id_water', field1, field2 FROM water_low_resolution
)
INSERT INTO STATS_NEW (sensor_id, ts, begin_state)
SELECT s.sensor_id, ROUND(field1, 0), ROUND(field2 / correction, 3)
FROM CTE_ALL_LOW_RESOLUTION
JOIN sensors s ON s.name = sensor_name
LEFT JOIN (
  SELECT sensor_id, MIN(ts) AS min_ts
  FROM STATS_NEW
  GROUP BY sensor_id
) m ON m.sensor_id = s.sensor_id
WHERE
  (field1 IS NOT NULL) AND (field2 IS NOT NULL) AND
  (field1 < COALESCE(m.min_ts, strftime('%s', 'now')))
GROUP BY sensor_name, field1;


/* Determine the end of the interval for the imported data */
WITH CTE_VALUE_STATS_VALUE AS (
  SELECT sensor_id, ts, (lead(begin_state, 1, 0) OVER (PARTITION BY sensor_id ORDER BY sensor_id, ts)) AS value
  FROM STATS_NEW
  ORDER BY sensor_id, ts
)
UPDATE STATS_NEW
SET end_state = CTE_VALUE_STATS_VALUE.value
FROM CTE_VALUE_STATS_VALUE
WHERE
  STATS_NEW.sensor_id = CTE_VALUE_STATS_VALUE.sensor_id AND
  STATS_NEW.ts = CTE_VALUE_STATS_VALUE.ts;

  
/* Remove any overlapping records from the imported data that are already in Home Assistant */
WITH CTE_SENSOR_MIN_TS(metadata_id, min_ts)  AS (
  SELECT metadata_id, MIN(start_ts) AS min_ts
  FROM statistics
  WHERE metadata_id in (SELECT sensor_id FROM SENSORS)
  GROUP BY metadata_id
)
DELETE FROM STATS_NEW
WHERE
STATS_NEW.ROWID IN (
  SELECT STATS_NEW.ROWID FROM STATS_NEW, CTE_SENSOR_MIN_TS
  WHERE
    STATS_NEW.sensor_id = CTE_SENSOR_MIN_TS.metadata_id AND
    STATS_NEW.ts >= CTE_SENSOR_MIN_TS.min_ts
);


/* Insert the data from Home Assistant so that we can adjust the records with the new calculated sum 
   Home Assistant records only have the end state of the interval
*/
INSERT INTO STATS_NEW (sensor_id, ts, end_state, old_sum)
SELECT metadata_id, start_ts, state, sum
FROM statistics
WHERE metadata_id IN (SELECT sensor_id FROM SENSORS);


/* Calculate the difference per interval
  - For the imported data, calculate the diff by subtracting the begin_state from the end_state (old_sum is NULL)
  - For the Home Assistant values, calculate the diff from the previous record from the existing sum column (old_sum is not NULL)
*/
UPDATE STATS_NEW
SET diff = end_state - begin_state
WHERE
  old_sum IS NULL;
  
WITH CTE_DIFF_STATS_SUM AS (
  SELECT sensor_id, ts, (old_sum - lag(old_sum, 1, 0) OVER (PARTITION BY sensor_id ORDER BY sensor_id, ts))  AS diff
  FROM STATS_NEW
  ORDER BY sensor_id, ts
)
UPDATE STATS_NEW
SET diff = CTE_DIFF_STATS_SUM.diff
FROM CTE_DIFF_STATS_SUM
WHERE
  STATS_NEW.sensor_id = CTE_DIFF_STATS_SUM.sensor_id AND
  STATS_NEW.ts = CTE_DIFF_STATS_SUM.ts AND
  STATS_NEW.old_sum IS NOT NULL;


/* Cleanup possible wrong values:
  - Diff is null  => The point where the imported data goes over to Home Assistant data 
  - Diff < 0  => Probably new meter installed (measurement should be low)
  - Diff > 1000 => Incorrect value 
  First handle the first two cases and then correct to 0 when incorrect value
*/
UPDATE STATS_NEW
SET diff = old_sum
WHERE
  diff IS NULL;

UPDATE STATS_NEW
SET diff = round(end_state, 3)
WHERE
  (diff < 0.0) AND
  (end_state < (SELECT cutoff_new_meter FROM SENSORS WHERE STATS_NEW.sensor_id = SENSORS.sensor_id LIMIT 1));

UPDATE STATS_NEW
SET diff = 0
WHERE
  (diff < 0.0) OR
  (diff > (SELECT cutoff_invalid_value FROM SENSORS WHERE STATS_NEW.sensor_id = SENSORS.sensor_id LIMIT 1));


/* Calculate the new sum
   It is calculated by calculating the sum up till the record that is currently processed
*/
WITH CTE_SUM_STATS AS (
  SELECT sensor_id, ts, SUM(diff) OVER (PARTITION BY sensor_id ORDER BY sensor_id, ts) AS new_sum
  FROM STATS_NEW
)
UPDATE STATS_NEW
SET new_sum = round(CTE_SUM_STATS.new_sum, 3)
FROM CTE_SUM_STATS
WHERE
  STATS_NEW.sensor_id = CTE_SUM_STATS.sensor_id AND
  STATS_NEW.ts = CTE_SUM_STATS.ts;


/* Copy the new information to the statistics table
id          => primary key and automatically filled with ROWID
state       => the end_state of the interval
sum         => calculated new_sum value
metadata_id => the fixed metadata id of this statistics (see top)
created_ts  => set to the timestamp of the statistic
start_ts    => timestamp of the statistic
The sum is updated in case the record is already in Home Assistant

"where true" is needed to remove parsing ambiguity
*/
INSERT INTO statistics (state, sum, metadata_id, created_ts, start_ts)
SELECT end_state, new_sum, sensor_id, ts, ts FROM STATS_NEW WHERE true
ON CONFLICT DO UPDATE SET sum = excluded.sum;


/* Also update the short term statistics. 
   We calculate the delta with which the sum was changed and add that to the current measurements
*/
WITH CTE_CORRECTION AS (
  SELECT DISTINCT metadata_id, first_value(new_sum - sum) OVER (PARTITION BY metadata_id ORDER BY start_ts DESC) AS correction_factor
  FROM
    statistics_short_term as SST, STATS_NEW AS SN
  WHERE
    SST.metadata_id = SN.sensor_id AND
    SST.start_ts = SN.ts
)
UPDATE statistics_short_term 
SET sum = sum + CTE_CORRECTION.correction_factor
FROM CTE_CORRECTION
WHERE
  statistics_short_term.metadata_id = CTE_CORRECTION.metadata_id;
  
/* Remove the temporary tables */
DROP TABLE IF EXISTS SENSORS;
DROP TABLE IF EXISTS STATS_NEW;

/* Remove the imported tables */
DROP TABLE IF EXISTS elec_feed_in_tariff_1_high_resolution;
DROP TABLE IF EXISTS elec_feed_in_tariff_2_high_resolution;
DROP TABLE IF EXISTS elec_feed_out_tariff_1_high_resolution;
DROP TABLE IF EXISTS elec_feed_out_tariff_2_high_resolution;
DROP TABLE IF EXISTS elec_solar_high_resolution;
DROP TABLE IF EXISTS elec_battery_feed_in_high_resolution;
DROP TABLE IF EXISTS elec_battery_feed_out_high_resolution;
DROP TABLE IF EXISTS gas_high_resolution;
DROP TABLE IF EXISTS water_high_resolution;

DROP TABLE IF EXISTS elec_feed_in_tariff_1_low_resolution;
DROP TABLE IF EXISTS elec_feed_in_tariff_2_low_resolution;
DROP TABLE IF EXISTS elec_feed_out_tariff_1_low_resolution;
DROP TABLE IF EXISTS elec_feed_out_tariff_2_low_resolution;
DROP TABLE IF EXISTS elec_solar_low_resolution;
DROP TABLE IF EXISTS elec_battery_feed_in_low_resolution;
DROP TABLE IF EXISTS elec_battery_feed_out_low_resolution;
DROP TABLE IF EXISTS gas_low_resolution;
DROP TABLE IF EXISTS water_low_resolution;