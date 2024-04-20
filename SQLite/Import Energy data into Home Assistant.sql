/* SQLite: Import energy/water data into Home Assistant */


/* Create a temp table to hold the used sensor metadata */
DROP TABLE IF EXISTS SENSORS;
CREATE TEMP TABLE SENSORS (name TEXT PRIMARY KEY, sensor_id INTEGER, correction FLOAT);
/* In case the provided data is in L and sensor is in m³ then the correction is 1000.0 (no correction -> 1.0) */
INSERT INTO SENSORS VALUES ('sensor_id_gas',					6,		1000.0);	/* Change */
/* In case the provided data is in Wh and sensor is in kWh then the correction is 1000.0 (no correction -> 1.0) */
INSERT INTO SENSORS VALUES ('sensor_id_elec_feed_in_tariff_1',	7,		1000.0);	/* Change */
/* In case the provided data is in Wh and sensor is in kWh then the correction is 1000.0 (no correction -> 1.0) */
INSERT INTO SENSORS VALUES ('sensor_id_elec_feed_in_tariff_2',	8,		1000.0);	/* Change */
/* In case the provided data is in Wh and sensor is in kWh then the correction is 1000.0 (no correction -> 1.0) */
INSERT INTO SENSORS VALUES ('sensor_id_elec_feed_out_tariff_1',	9,		1000.0);	/* Change */
/* In case the provided data is in Wh and sensor is in kWh then the correction is 1000.0 (no correction -> 1.0) */
INSERT INTO SENSORS VALUES ('sensor_id_elec_feed_out_tariff_2',	10,		1000.0);	/* Change */
/* In case the provided data is in Wh and sensor is in kWh then the correction is 1000.0 (no correction -> 1.0) */
INSERT INTO SENSORS VALUES ('sensor_id_elec_solar',				352,	1000.0);	/* Change */
/* In case the provided data is in L and sensor is in m³ then the correction is 1000.0 (no correction -> 1.0) */
INSERT INTO SENSORS VALUES ('sensor_id_water',					653,	1000.0);	/* Change */


/* Create a temp table to hold some variables (SQLite does not support variables so this is a workaround) */
DROP TABLE IF EXISTS VARS;
CREATE TEMP TABLE VARS (name TEXT PRIMARY KEY, value FLOAT);
INSERT INTO VARS VALUES ('cutoff_new_meter', 25);	/* Change this in case your new meter started with a higher start value (especially when the unit_of_measurement is not kWh!)	*/
INSERT INTO VARS VALUES ('cutoff_invalid_value', 1000);	/* Change this in case a higher/lower diff cutoff is needed to mark a value invalid												*/


/* FOR NORMAL USAGE THERE SHOULD BE NO CHANGES NEEDED AFTER THIS POINT */


/* Create empty temp import tables if they do not exist so that the SQL statements do not break in case the table is not imported */
CREATE TABLE IF NOT EXISTS elec_feed_in_tariff_1_high_resolution	(field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_in_tariff_1 
CREATE TABLE IF NOT EXISTS elec_feed_in_tariff_1_low_resolution		(field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_in_tariff_1 
CREATE TABLE IF NOT EXISTS elec_feed_in_tariff_2_high_resolution	(field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_in_tariff_2
CREATE TABLE IF NOT EXISTS elec_feed_in_tariff_2_low_resolution		(field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_in_tariff_2
CREATE TABLE IF NOT EXISTS elec_feed_out_tariff_1_high_resolution	(field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_out_tariff_1
CREATE TABLE IF NOT EXISTS elec_feed_out_tariff_1_low_resolution	(field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_out_tariff_1
CREATE TABLE IF NOT EXISTS elec_feed_out_tariff_2_high_resolution	(field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_out_tariff_2
CREATE TABLE IF NOT EXISTS elec_feed_out_tariff_2_low_resolution	(field1 FLOAT, field2 FLOAT); -- sensor_id_elec_feed_out_tariff_2
CREATE TABLE IF NOT EXISTS elec_solar_high_resolution				(field1 FLOAT, field2 FLOAT); -- sensor_id_elec_solar
CREATE TABLE IF NOT EXISTS elec_solar_low_resolution				(field1 FLOAT, field2 FLOAT); -- sensor_id_elec_solar
CREATE TABLE IF NOT EXISTS gas_high_resolution						(field1 FLOAT, field2 FLOAT); -- sensor_id_gas
CREATE TABLE IF NOT EXISTS gas_low_resolution						(field1 FLOAT, field2 FLOAT); -- sensor_id_gas
CREATE TABLE IF NOT EXISTS water_high_resolution					(field1 FLOAT, field2 FLOAT); -- sensor_id_water
CREATE TABLE IF NOT EXISTS water_low_resolution						(field1 FLOAT, field2 FLOAT); -- sensor_id_water

/* Create temp tables that can hold the difference between the measurements and create a new sum */
DROP TABLE IF EXISTS STATS_NEW;
CREATE TEMP TABLE STATS_NEW (
	sensor_id	INTEGER,
	ts			FLOAT,
	value		FLOAT,
	diff		FLOAT,
	old_sum		FLOAT,
	new_sum		FLOAT
);


/* Insert the high resolution records and apply the correction */
INSERT INTO STATS_NEW (sensor_id, ts, value)
SELECT
	(SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_elec_feed_in_tariff_1' LIMIT 1),
	round(field1, 0),
	round(field2 / (SELECT correction FROM SENSORS WHERE name = 'sensor_id_elec_feed_in_tariff_1' LIMIT 1), 3)
FROM elec_feed_in_tariff_1_high_resolution;

INSERT INTO STATS_NEW (sensor_id, ts, value)
SELECT
	(SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_elec_feed_in_tariff_2' LIMIT 1),
	round(field1, 0),
	round(field2 / (SELECT correction FROM SENSORS WHERE name = 'sensor_id_elec_feed_in_tariff_2' LIMIT 1), 3)
FROM elec_feed_in_tariff_2_high_resolution;

INSERT INTO STATS_NEW (sensor_id, ts, value)
SELECT
	(SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_elec_feed_out_tariff_1' LIMIT 1),
	round(field1, 0),
	round(field2 / (SELECT correction FROM SENSORS WHERE name = 'sensor_id_elec_feed_out_tariff_1' LIMIT 1), 3)
FROM elec_feed_out_tariff_1_high_resolution;

INSERT INTO STATS_NEW (sensor_id, ts, value)
SELECT
	(SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_elec_feed_out_tariff_2' LIMIT 1),
	round(field1, 0),
	round(field2 / (SELECT correction FROM SENSORS WHERE name = 'sensor_id_elec_feed_out_tariff_2' LIMIT 1), 3)
FROM elec_feed_out_tariff_2_high_resolution;

INSERT INTO STATS_NEW (sensor_id, ts, value)
SELECT
	(SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_elec_solar' LIMIT 1),
	round(field1, 0),
	round(field2 / (SELECT correction FROM SENSORS WHERE name = 'sensor_id_elec_solar' LIMIT 1), 3)
FROM elec_solar_high_resolution;

INSERT INTO STATS_NEW (sensor_id, ts, value)
SELECT
	(SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_gas' LIMIT 1),
	round(field1, 0),
	round(field2 / (SELECT correction FROM SENSORS WHERE name = 'sensor_id_gas' LIMIT 1), 3)
FROM gas_high_resolution;

INSERT INTO STATS_NEW (sensor_id, ts, value)
SELECT
	(SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_water' LIMIT 1),
	round(field1, 0),
	round(field2 / (SELECT correction FROM SENSORS WHERE name = 'sensor_id_water' LIMIT 1), 3)
FROM water_high_resolution;


/* Insert the low resolution records and apply the correction.
   We only add data that is older than the high resolution records
*/
INSERT INTO STATS_NEW (sensor_id, ts, value)
SELECT
	(SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_elec_feed_in_tariff_1' LIMIT 1),
	round(field1, 0),
	round(field2 / (SELECT correction FROM SENSORS WHERE name = 'sensor_id_elec_feed_in_tariff_1' LIMIT 1), 3)
FROM elec_feed_in_tariff_1_low_resolution  
WHERE
  field1 < (SELECT COALESCE(MIN(ts), strftime('%s', 'now')) FROM STATS_NEW WHERE sensor_id = (SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_elec_feed_in_tariff_1' LIMIT 1));

INSERT INTO STATS_NEW (sensor_id, ts, value)
SELECT
	(SELECT sensor_id FROM SENSORS WHERE Name = 'sensor_id_elec_feed_in_tariff_2' LIMIT 1),
	round(field1, 0),
	round(field2 / (SELECT correction FROM SENSORS WHERE name = 'sensor_id_elec_feed_in_tariff_2' LIMIT 1), 3)
FROM elec_feed_in_tariff_2_low_resolution  
WHERE
  field1 < (SELECT COALESCE(MIN(ts), strftime('%s', 'now')) FROM STATS_NEW WHERE sensor_id = (SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_elec_feed_in_tariff_2' LIMIT 1));

INSERT INTO STATS_NEW (sensor_id, ts, value)
SELECT
	(SELECT sensor_id FROM SENSORS WHERE Name = 'sensor_id_elec_feed_out_tariff_1' LIMIT 1),
	round(field1, 0),
	round(field2 / (SELECT correction FROM SENSORS WHERE name = 'sensor_id_elec_feed_out_tariff_1' LIMIT 1), 3)
FROM elec_feed_out_tariff_1_low_resolution  
WHERE
  field1 < (SELECT COALESCE(MIN(ts), strftime('%s', 'now')) FROM STATS_NEW WHERE sensor_id = (SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_elec_feed_out_tariff_1' LIMIT 1));

INSERT INTO STATS_NEW (sensor_id, ts, value)
SELECT
	(SELECT sensor_id FROM SENSORS WHERE Name = 'sensor_id_elec_feed_out_tariff_2' LIMIT 1),
	round(field1, 0),
	round(field2 / (SELECT correction FROM SENSORS WHERE name = 'sensor_id_elec_feed_out_tariff_2' LIMIT 1), 3)
FROM elec_feed_out_tariff_2_low_resolution  
WHERE
  field1 < (SELECT COALESCE(MIN(ts), strftime('%s', 'now')) FROM STATS_NEW WHERE sensor_id = (SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_elec_feed_out_tariff_2' LIMIT 1));

INSERT INTO STATS_NEW (sensor_id, ts, value)
SELECT
	(SELECT sensor_id FROM SENSORS WHERE Name = 'sensor_id_elec_solar' LIMIT 1),
	round(field1, 0),
	round(field2 / (SELECT correction FROM SENSORS WHERE name = 'sensor_id_elec_solar' LIMIT 1), 3)
FROM elec_solar_low_resolution  
WHERE
  field1 < (SELECT COALESCE(MIN(ts), strftime('%s', 'now')) FROM STATS_NEW WHERE sensor_id = (SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_elec_solar' LIMIT 1));

INSERT INTO STATS_NEW (sensor_id, ts, value)
SELECT
	(SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_gas' LIMIT 1),
	round(field1, 0),
	round(field2 / (SELECT correction FROM SENSORS WHERE name = 'sensor_id_gas' LIMIT 1), 3)
FROM gas_low_resolution  
WHERE
  field1 < (SELECT COALESCE(MIN(ts), strftime('%s', 'now')) FROM STATS_NEW WHERE sensor_id = (SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_gas' LIMIT 1));

INSERT INTO STATS_NEW (sensor_id, ts, value)
SELECT
	(SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_water' LIMIT 1),
	round(field1, 0),
	round(field2 / (SELECT correction FROM SENSORS WHERE name = 'sensor_id_water' LIMIT 1), 3)
FROM water_low_resolution  
WHERE
  field1 < (SELECT COALESCE(MIN(ts), strftime('%s', 'now')) FROM STATS_NEW WHERE sensor_id = (SELECT sensor_id FROM SENSORS WHERE name = 'sensor_id_water' LIMIT 1));

  
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


/* Insert the data from Home Assistant so that we can adjust the records with the new calculated sum */
INSERT INTO STATS_NEW (sensor_id, ts, value, old_sum)
SELECT metadata_id, start_ts, state, sum
FROM statistics
WHERE metadata_id IN (SELECT sensor_id FROM SENSORS);


/* Calculate the difference from the previous record in the table 
  - For the imported data calculate the diff from the previous record from the imported values (use value column / old_sum column is empty)
  - For the Home Assistant values calculate the diff from the previous record from the existing sum column (use old_sum column / old_sum column is not empty)
*/
WITH CTE_DIFF_STATS_VALUE AS (
	SELECT sensor_id, ts, round(value - (lag(value, 1, 0) OVER (PARTITION BY sensor_id ORDER BY sensor_id, ts)), 3) AS diff
	FROM STATS_NEW
	ORDER BY sensor_id, ts
)
UPDATE STATS_NEW
SET diff = CTE_DIFF_STATS_VALUE.diff
FROM CTE_DIFF_STATS_VALUE
WHERE
  STATS_NEW.sensor_id = CTE_DIFF_STATS_VALUE.sensor_id AND
  STATS_NEW.ts = CTE_DIFF_STATS_VALUE.ts AND
  STATS_NEW.old_sum IS NULL;

WITH CTE_DIFF_STATS_SUM AS (
	SELECT sensor_id, ts, old_sum - (lag(old_sum, 1, 0) OVER (PARTITION BY sensor_id ORDER BY sensor_id, ts)) AS diff
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
        - Remove the first record if no diff could be determined (imported data)
        - Diff is null  => The point where the imported data goes over to Home Assistant data 
		- Diff < 0		=> Probably new meter installed (measurement should be low)
		- Diff > 1000	=> Incorrect value 
   First handle the first two cases and then correct to 0 when incorrect value
*/
DELETE FROM STATS_NEW
WHERE
ROWID IN (
	SELECT first_value(ROWID) OVER (PARTITION BY sensor_id ORDER BY sensor_id, ts) AS ROWID FROM STATS_NEW
	WHERE old_sum IS NULL
);

UPDATE STATS_NEW
SET diff = round(old_sum, 3)
WHERE (diff IS NULL);

UPDATE STATS_NEW
SET diff = round(value, 3)
WHERE (diff < 0.0) AND (value < (SELECT value FROM VARS WHERE Name = 'cutoff_new_meter' LIMIT 1));

UPDATE STATS_NEW
SET diff = 0
WHERE (diff < 0.0) OR (diff > (SELECT value FROM VARS WHERE Name = 'cutoff_invalid_value' LIMIT 1));


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
id			=> primary key and automatically filled with ROWID
sum			=> calculated new_sum value
metadata_id	=> the fixed metadata id of this statistics (see top)
created_ts	=> set to the timestamp of the statistic
start_ts	=> timestamp of the statistic
The sum is updated in case the record is already in Home Assistant

"where true" is needed to remove parsing ambiguity
*/
INSERT INTO statistics (state, sum, metadata_id, created_ts, start_ts)
SELECT new_sum, new_sum, sensor_id, ts, ts FROM STATS_NEW WHERE true
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
DROP TABLE IF EXISTS VARS;
DROP TABLE IF EXISTS STATS_NEW;

/* Remove the imported tables */
DROP TABLE IF EXISTS elec_feed_in_tariff_1_high_resolution;
DROP TABLE IF EXISTS elec_feed_in_tariff_2_high_resolution;
DROP TABLE IF EXISTS elec_feed_out_tariff_1_high_resolution;
DROP TABLE IF EXISTS elec_feed_out_tariff_2_high_resolution;
DROP TABLE IF EXISTS elec_solar_high_resolution;
DROP TABLE IF EXISTS elec_feed_in_tariff_1_low_resolution;
DROP TABLE IF EXISTS elec_feed_in_tariff_2_low_resolution;
DROP TABLE IF EXISTS elec_feed_out_tariff_1_low_resolution;
DROP TABLE IF EXISTS elec_feed_out_tariff_2_low_resolution;
DROP TABLE IF EXISTS elec_solar_low_resolution;
DROP TABLE IF EXISTS gas_high_resolution;
DROP TABLE IF EXISTS gas_low_resolution;
DROP TABLE IF EXISTS water_high_resolution;
DROP TABLE IF EXISTS water_low_resolution;