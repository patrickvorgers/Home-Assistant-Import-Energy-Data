/* SQLite: Cleanup the backup data after the imnport script has been executed */


/* Drop the backup tables */
DROP TABLE IF EXISTS BACKUP_STATISTICS;
DROP TABLE IF EXISTS BACKUP_STATISTICS_SHORT_TERM;