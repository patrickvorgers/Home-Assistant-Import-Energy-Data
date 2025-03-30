/* SQLite: Restore the backup data after the imnport script has been executed */


/* Delete the imported records in statistics */
DELETE FROM statistics
WHERE id IN (
  SELECT s.id
  FROM statistics s
  WHERE s.metadata_id IN (
    SELECT DISTINCT metadata_id FROM BACKUP_STATISTICS
  )
  AND NOT EXISTS (
    SELECT 1
    FROM BACKUP_STATISTICS b
    WHERE b.id = s.id
  )
);


/* Delete the imported records in statistics_short_term */
DELETE FROM statistics_short_term
WHERE id IN (
  SELECT sst.id
  FROM statistics_short_term sst
  WHERE sst.metadata_id IN (
    SELECT DISTINCT metadata_id FROM BACKUP_STATISTICS_SHORT_TERM
  )
  AND NOT EXISTS (
    SELECT 1
    FROM BACKUP_STATISTICS_SHORT_TERM bst
    WHERE bst.id = sst.id
  )
);


/* Restore the sum field in statistics from BACKUP_STATISTICS */
UPDATE statistics
SET "sum" = (
  SELECT b."sum"
  FROM BACKUP_STATISTICS b
  WHERE b.id = statistics.id
)
WHERE id IN (
  SELECT id FROM BACKUP_STATISTICS
);


/* Restore the sum field in statistics_short_term from BACKUP_STATISTICS_SHORT_TERM */
UPDATE statistics_short_term
SET "sum" = (
  SELECT bst."sum"
  FROM BACKUP_STATISTICS_SHORT_TERM bst
  WHERE bst.id = statistics_short_term.id
)
WHERE id IN (
  SELECT id FROM BACKUP_STATISTICS_SHORT_TERM
);