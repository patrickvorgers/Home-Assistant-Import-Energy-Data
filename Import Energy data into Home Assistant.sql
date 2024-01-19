/* 
Import energy data into Home Assistant

HOW-TO:

Tooling
- Download and install: DB Browser (64 bit) for SQLite https://sqlitebrowser.org/ (tested windows version 3.12.2)
- Download and install/configure: WinSCP (https://winscp.net/eng/download.php)

Source data preparation
- Check whether a script/how-to exists for your provider (datasources directory)
	Script/how-to exists:
		Follow how-to to prepare the needed CSV files
	Script/How-to does not exist:
		Determine how to get the data from your energy provider (download/API etc.)
		Get the data from the energy provider using the identified method
		Convert the data in the needed CSV files. The definition for the CSV files is very simple. Each row contains: Epoch Unix Timestamp, sensor value
			Example:
				1540634400,8120605
				1540638000,8120808
				1540641600,8120993
				1540645200,8121012
		Depending on the used sensors determine which CSV data files need to be created:
			elec_feed_in_tariff_1_high_resolution.csv
				Contains the highest resolution usage data available (for instance: hour resolution)
				Used in case there is only one tariff
			elec_feed_in_tariff_1_low_resolution.csv
				Contains the lowest resolution usage data available (for instance: day resolution)
				Used in case there is only one tariff
				Not needed in case that there is only one resolution available.
			elec_feed_in_tariff_2_high_resolution.csv
				Contains the highest resolution usage data available (for instance: hour resolution)
				Not needed in case that there is only one tariff available.
			elec_feed_in_tariff_2_low_resolution.csv
				Contains the lowest resolution usage data available (for instance: day resolution)
				Not needed in case that there is only one tariff available.
				Not needed in case that there is only one resolution available.
			elec_feed_out_tariff_1_high_resolution.csv
				Contains the highest resolution production data available (for instance: hour resolution)
				Used in case there is only one tariff
				Not needed in case that there is no production (for instance: no solar panels, no battery export)
			elec_feed_out_tariff_1_low_resolution.csv
				Contains the lowest resolution production data available (for instance: day resolution).
				Used in case there is only one tariff
				Not needed in case that there is no production (for instance: no solar panels, no battery export)
				Not needed in case that there is only one resolution available.
			elec_feed_out_tariff_2_high_resolution.csv
				Contains the highest resolution production data available (for instance: hour resolution).
				Not needed in case that there is no production (for instance: no solar panels, no battery export)
				Not needed in case that there is only one tariff available.
			elec_feed_out_tariff_2_low_resolution.csv
				Contains the lowest resolution production data available (for instance: day resolution).
				Not needed in case that there is no production (for instance: no solar panels, no battery export)
				Not needed in case that there is only one tariff available.
				Not needed in case that there is only one resolution available.
			elec_solar_high_resolution.csv
				Contains the highest resolution production data available (for instance: hour resolution)
				Not needed in case that there are no solar panels
			elec_solar_low_resolution.csv	
				Contains the lowest resolution production data available (for instance: day resolution)
				Not needed in case that there are no solar panels
				Not needed in case that there is only one resolution available.
			gas_high_resolution.csv			
				Contains the highest resolution production data available (for instance: hour resolution).
				Not needed in case that there is no gas usage
			gas_low_resolution.csv
				Contains the lowest resolution production data available (for instance: day resolution).
				Not needed in case that there is no gas usage
				Not needed in case that there is only one resolution available.

Home Assistant preparation
- Create a backup of the Home Assistant database
	Disable recorder while making the backup -> Developer tools/Services/Call service: Recorder:disable
- Download the created backup
- Stop the Home Assistant core
	Developer tools/Services/Call service: Home Assistant Core Integration: Stop
- Home Assistant data: 
	extract: "home-assistant_v2.db" (from "backup.tar" extract "homeassistant.tar.gz" from "data" folder)
	As an alternative it is also possible to download the "home-assistant_v2.db" directly from the Home Assistant "config" directory (For example: use WinSCP in combination with the Home Assistant SSH addon).
	In case of this method make sure that you didn't skip the step to create a backup so that you can always restore this version of the database!

Import the data
- Start "DB Browser for SQLite"
- Open project "Import Energy data into Home Assistant.sqbpro". If the database is not loaded directly you have to open the "home-assistant_v2.db" database manually ("Open Database").
- Validate the schema version of the database (Browse Data -> Table: schema_version)
  The script has been tested with schema version 42. With higher versions you should validate if the structure of the "statistics" and "short_term_statistics" tables have changed.
  used fields in table "statistics": metadata_id, state, sum, start_ts, created_ts
  used fields in table "short_term_statistics": sum
- Import, one at a time, all the created CSV data elec* and gas* files (File -> Import -> Table from CSV file...)
  It is possible to load data from multiple CSV's with the same name. The data of the second import is than added to the existing tables.
  This can be used in case there are multiple energy source providers for different timeperiods. In this case you first import the files from the first energy provider and than then second etc.
- Lookup in the "statistics_meta" table the ID's of the sensors (Browse Data -> Table: statistics_meta; You can use "filter" to find the id of the sensor)
  The names of the sensors can be looked up in the Home Assistant Energy dashboard (Settings -> Dashboards -> Energy).
  Example:
 	id  statistic_id                                	source      unit_of_measurement
	6	sensor.gas_meter								recorder	m³
	7	sensor.electricity_meter_feed_in_tariff_1		recorder	kWh
	8	sensor.electricity_meter_feed_in_tariff_2		recorder	kWh
	9	sensor.electricity_meter_feed_out_tariff_1		recorder	kWh
	10	sensor.electricity_meter_feed_out_tariff_2		recorder	kWh
	352	sensor.solar_energy_produced_today				recorder	kWh
- Change the script below and remove/comment out the lines of the sensors that are not needed.
  They can be found at the top of the script by looking up the lines where "* Change *" has been added in the SQL statement.
- Change the script below and update the ID's according to the found ID's in the "statistics_meta" table.
  They can be found at the top of the script by looking up the lines where "* Change *" has been added in the SQL statement.
  Determine also the correction factor in case the unit_of_measurement of the sensor differs from the provided data. The unit of measurement of the datasource can be found in the readme of the datasource.
- Execute the SQL and wait for it to complete. (Please be patient because this can take some time!)
- Commit the changes by selecting "Write changes" in the toolbar, if the script ends without errors. In case of an error select "Revert changes" and correct the error and execute the script again.

Replace Home Assistant database
- Make sure that the Home Assistant core is still stopped (Home Assistant UI does not respond)
- Upload "home-assistant_v2.db" to the Home Assistant "config" directory (For example: use WinSCP in combination with the Home Assistant SSH addon). 
- Restart/reboot Home Assistant (physically reboot Home Assistant or login using PUTTY-SSH and execute the "reboot" command)
- Validate the imported data in the "Energy Dashboard"
- Enjoy :-)


Background information:

Normal tariff meter values without correction for solar usage
elec_feed_in_tariff_1_high_resolution.csv (for instance: hourly)
elec_feed_in_tariff_1_low_resolution.csv (for instance: daily)

Low tariff meter values without correction for solar usage
elec_feed_in_tariff_2_high_resolution.csv (for instance: hourly)
elec_feed_in_tariff_2_low_resolution.csv (for instance: daily)

Normal tariff production meter values 
elec_feed_out_tariff_1_high_resolution.csv (for instance: hourly)
elec_feed_out_tariff_1_low_resolution.csv (for instance: daily)

Low tariff production meter values
elec_feed_out_tariff_2_high_resolution.csv (for instance: hourly)
elec_feed_out_tariff_2_low_resolution.csv (for instance: daily)

Solar production meter values
elec_solar_high_resolution.csv (for instance: hourly)
elec_solar_low_resolution.csv (for instance: daily)

Gas meter values
gas_high_resolution.csv (for instance: hourly)
gas_low_resolution.csv (for instance: daily)


Daily reset of values is also handled by the script. This is the same case as a new meter.
Long term statistics (1 hour interval) => statistics
Short term statistics (5 min interval) => statistics_short_term

Short term statistics are rolled over to long term statistics.
Both tables need to be updated according to the new imported data which changes the sum column!

*/

/* Create a temp table to hold the used sensor metadata */
DROP TABLE IF EXISTS SENSORS;
CREATE TEMP TABLE SENSORS (name TEXT PRIMARY KEY, sensor_id INTEGER, correction FLOAT);
/* In case the provided data is in L and sensor is in m³ then the correction is 1000.0 */
INSERT INTO SENSORS VALUES ('sensor_id_gas',					6,		1000.0);	/* Change */
/* In case the provided data is in Wh and sensor is in kWh then the correction is 1000.0 */
INSERT INTO SENSORS VALUES ('sensor_id_elec_feed_in_tariff_1',	7,		1000.0);	/* Change */
/* In case the provided data is in Wh and sensor is in kWh then the correction is 1000.0 */
INSERT INTO SENSORS VALUES ('sensor_id_elec_feed_in_tariff_2',	8,		1000.0);	/* Change */
/* In case the provided data is in Wh and sensor is in kWh then the correction is 1000.0 */
INSERT INTO SENSORS VALUES ('sensor_id_elec_feed_out_tariff_1',	9,		1000.0);	/* Change */
/* In case the provided data is in Wh and sensor is in kWh then the correction is 1000.0 */
INSERT INTO SENSORS VALUES ('sensor_id_elec_feed_out_tariff_2',	10,		1000.0);	/* Change */
/* In case the provided data is in Wh and sensor is in kWh then the correction is 1000.0 */
INSERT INTO SENSORS VALUES ('sensor_id_elec_solar',				352,	1000.0);	/* Change */


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
id		=> primary key and automatically filled with ROWID
sum		=> calculated new_sum value
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