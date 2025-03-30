/* MariaDB: Import Energy data into Home Assistant */


/* Start a transaction so that we can rollback any changes if needed */
ROLLBACK;
START TRANSACTION;

/* Disable warnings: The IF EXISTS clause triggers a warning when the table does not exist */ 
SET sql_notes = 0;

/* Create a temp table to hold the used sensor metadata */
DROP TEMPORARY TABLE IF EXISTS SENSORS;
CREATE TEMPORARY TABLE SENSORS (name VARCHAR(255) PRIMARY KEY, sensor_id INTEGER, correction FLOAT, cutoff_new_meter FLOAT, cutoff_invalid_value FLOAT);

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
INSERT INTO SENSORS VALUES ('gas',                    6,        1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('elec_feed_in_tariff_1',  7,        1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('elec_feed_in_tariff_2',  8,        1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('elec_feed_out_tariff_1', 9,        1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('elec_feed_out_tariff_2', 10,       1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('elec_solar',             352,      1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('elec_battery_feed_in',   450,      1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('elec_battery_feed_out',  451,      1000.0,    25.0,            1000.0); /* Change */
INSERT INTO SENSORS VALUES ('water',                  653,      1000.0,    25.0,            1000.0); /* Change */


/* FOR NORMAL USAGE THERE SHOULD BE NO CHANGES NEEDED AFTER THIS POINT */


/* Create a temp table that can hold the difference between the measurements and create a new sum */
DROP TEMPORARY TABLE IF EXISTS STATS_NEW;
CREATE TEMPORARY TABLE STATS_NEW (
  id            INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
  sensor_id     INTEGER NOT NULL,
  ts            DOUBLE NOT NULL,
  begin_state   DOUBLE,
  end_state     DOUBLE,
  diff          DOUBLE,
  old_sum       DOUBLE,
  new_sum       DOUBLE
);
CREATE UNIQUE INDEX idx_sensor_id_ts ON STATS_NEW (sensor_id, ts);


/* Insert the high resolution records and apply the correction 

   The values are the start of the interval
*/
INSERT INTO STATS_NEW (sensor_id, ts, begin_state)
SELECT s.sensor_id, ROUND(imd.timestamp, 0), ROUND(imd.value / s.correction, 3)
FROM IMPORT_DATA AS imd
JOIN SENSORS AS s ON s.name = imd.id
WHERE
  imd.resolution = 'HIGH';


/* Insert the low resolution records and apply the correction.
   We only add data that is older than the high resolution records

   The values are the start of the interval
*/
INSERT INTO STATS_NEW (sensor_id, ts, begin_state)
SELECT s.sensor_id, ROUND(imd.timestamp, 0), ROUND(imd.value / s.correction, 3)
FROM IMPORT_DATA AS imd
JOIN SENSORS AS s ON s.name = imd.id
LEFT JOIN (
  SELECT sensor_id, MIN(ts) AS min_ts
  FROM STATS_NEW
  GROUP BY sensor_id
) AS m ON m.sensor_id = s.sensor_id
WHERE
  imd.resolution = 'LOW' AND
  imd.timestamp < COALESCE(m.min_ts, UNIX_TIMESTAMP());


/* Determine the end of the interval for the imported data */
UPDATE STATS_NEW,
  (SELECT sensor_id, ts, LEAD(begin_state, 1) OVER (PARTITION BY sensor_id ORDER BY sensor_id, ts) AS value
    FROM STATS_NEW
    ORDER BY sensor_id, ts) AS NEXT_VALUES
SET STATS_NEW.end_state = NEXT_VALUES.value
WHERE
  STATS_NEW.sensor_id = NEXT_VALUES.sensor_id AND
  STATS_NEW.ts = NEXT_VALUES.ts;


/* Remove any overlapping records from the imported data that are already in Home Assistant */
DELETE STATS_NEW
FROM STATS_NEW
JOIN (
  SELECT metadata_id, MIN(start_ts) AS min_ts
  FROM statistics
  WHERE
    metadata_id IN (SELECT sensor_id FROM SENSORS)
  GROUP BY metadata_id
) SENSOR_MIN_TS ON STATS_NEW.sensor_id = SENSOR_MIN_TS.metadata_id
WHERE
  STATS_NEW.ts >= SENSOR_MIN_TS.min_ts;


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

UPDATE STATS_NEW,
  (SELECT sensor_id, ts, (old_sum - lag(old_sum, 1) OVER (PARTITION BY sensor_id ORDER BY sensor_id, ts)) AS diff
   FROM STATS_NEW
   ORDER BY sensor_id, ts) AS DIFF_STATS_SUM
SET STATS_NEW.diff = DIFF_STATS_SUM.diff
WHERE
  STATS_NEW.sensor_id = DIFF_STATS_SUM.sensor_id AND
  STATS_NEW.ts = DIFF_STATS_SUM.ts AND
  STATS_NEW.old_sum IS NOT NULL;


/* Cleanup possible wrong values:
  - Diff is null  => The point where the imported data goes over to Home Assistant data 
  - Diff < 0   => Probably new meter installed (measurement should be low)
  - Diff > invalid => Incorrect value 
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
UPDATE STATS_NEW,
  (SELECT sensor_id, ts, SUM(diff) OVER (PARTITION BY sensor_id ORDER BY sensor_id, ts) AS new_sum
   FROM STATS_NEW) AS SUM_STATS
SET STATS_NEW.new_sum = round(SUM_STATS.new_sum, 3)
WHERE
  STATS_NEW.sensor_id = SUM_STATS.sensor_id AND
  STATS_NEW.ts = SUM_STATS.ts;


/* Copy records from the original tables into the backup tables
   We only copy the records for the sensors that are defined in SENSORS
*/
DROP TABLE IF EXISTS BACKUP_STATISTICS;
CREATE TABLE BACKUP_STATISTICS (id INTEGER PRIMARY KEY, metadata_id INTEGER, sum FLOAT);
CREATE INDEX idx_statistics_metadata_id ON BACKUP_STATISTICS (metadata_id);

INSERT INTO BACKUP_STATISTICS
SELECT id, metadata_id, sum FROM statistics
WHERE
  metadata_id IN (SELECT sensor_id FROM SENSORS);

DROP TABLE IF EXISTS BACKUP_STATISTICS_SHORT_TERM;
CREATE TABLE BACKUP_STATISTICS_SHORT_TERM (id INTEGER PRIMARY KEY, metadata_id INTEGER, sum FLOAT);
CREATE INDEX idx_statistics_short_term_metadata_id ON BACKUP_STATISTICS_SHORT_TERM (metadata_id);

INSERT INTO BACKUP_STATISTICS_SHORT_TERM
SELECT id, metadata_id, sum FROM statistics_short_term 
WHERE
  metadata_id IN (SELECT sensor_id FROM SENSORS);

  
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
SELECT end_state, new_sum, sensor_id, ts, ts FROM STATS_NEW
ON DUPLICATE KEY UPDATE sum = VALUES(sum);


/* Also update the short term statistics. 
   We calculate the delta with which the sum was changed and add that to the current measurements
   Remark: use WHERE TRUE to supress any warnings
*/
UPDATE statistics_short_term AS SST
JOIN (
  SELECT metadata_id, FIRST_VALUE(SN.new_sum - SST.sum) OVER (PARTITION BY SST.metadata_id ORDER BY SST.start_ts DESC) AS correction_factor
  FROM statistics_short_term AS SST
  JOIN STATS_NEW AS SN ON SST.metadata_id = SN.sensor_id AND SST.start_ts = SN.ts
  GROUP BY metadata_id
) AS CORRECTION ON SST.metadata_id = CORRECTION.metadata_id
SET SST.sum = SST.sum + CORRECTION.correction_factor
WHERE TRUE;


/* Remove the temporary tables */
DROP TEMPORARY TABLE IF EXISTS SENSORS;
DROP TEMPORARY TABLE IF EXISTS STATS_NEW;
DROP TABLE IF EXISTS IMPORT_DATA;

/* Do not drop the backup tables. They can be deleted after verification by the user. */

/* Enable the warnings again */
SET sql_notes = 1; 

/* Commit the changes - can be commented out while testing */
COMMIT;