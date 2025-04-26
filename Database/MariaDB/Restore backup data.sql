/* MariaDB: Restore the backup data after the imnport script has been executed */


/* Start a transaction so that we can rollback any changes if needed */
START TRANSACTION;


/* Delete the imported records in statistics */
DELETE s
FROM statistics s
LEFT JOIN BACKUP_STATISTICS b ON s.id = b.id
WHERE
  b.id IS NULL AND
  s.metadata_id IN (SELECT DISTINCT metadata_id FROM BACKUP_STATISTICS);


/* Delete the imported records in statistics_short_term */
DELETE sst
FROM statistics_short_term sst
LEFT JOIN BACKUP_STATISTICS_SHORT_TERM bst ON sst.id = bst.id
WHERE
  bst.id IS NULL AND
  sst.metadata_id IN (SELECT DISTINCT metadata_id FROM BACKUP_STATISTICS_SHORT_TERM);


/* Restore the sum field in statistics from BACKUP_STATISTICS */
UPDATE statistics s
JOIN BACKUP_STATISTICS b ON s.id = b.id
SET s.`sum` = b.`sum`;


/* Restore the sum field in statistics_short_term from BACKUP_STATISTICS_SHORT_TERM */
UPDATE statistics_short_term sst
JOIN BACKUP_STATISTICS_SHORT_TERM bst ON sst.id = bst.id
SET sst.`sum` = bst.`sum`;


/* Commit the changes */
COMMIT;