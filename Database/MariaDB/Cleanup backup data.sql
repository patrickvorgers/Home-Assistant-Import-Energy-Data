/* MariaDB: Cleanup the backup data after the imnport script has been executed */


/* Start a transaction so that we can rollback any changes if needed */
START TRANSACTION;

/* Disable warnings: The IF EXISTS clause triggers a warning when the table does not exist */ 
SET sql_notes = 0;

/* Drop the backup tables */
DROP TABLE IF EXISTS BACKUP_STATISTICS;
DROP TABLE IF EXISTS BACKUP_STATISTICS_SHORT_TERM;

/* Enable the warnings again */
SET sql_notes = 1; 

/* Commit the changes */
COMMIT;