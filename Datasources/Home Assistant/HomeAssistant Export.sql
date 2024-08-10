/* Get the history of an sensor from the statistics table */
SELECT CAST(start_ts AS INT) AS start_ts, state FROM statistics
WHERE
metadata_id = 6 /* Change */
ORDER BY start_ts