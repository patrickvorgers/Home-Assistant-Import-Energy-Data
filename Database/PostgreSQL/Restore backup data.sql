-- PostgreSQL: Restore the backup data after the import script has been executed

-- Start a transaction so that we can rollback any changes if needed
BEGIN;

-- Delete the imported records in statistics
DELETE FROM statistics s
USING backup_statistics b
WHERE s.metadata_id IN (SELECT DISTINCT metadata_id FROM backup_statistics)
  AND s.id NOT IN (SELECT id FROM backup_statistics);

-- Delete the imported records in statistics_short_term
DELETE FROM statistics_short_term sst
USING backup_statistics_short_term bst
WHERE sst.metadata_id IN (SELECT DISTINCT metadata_id FROM backup_statistics_short_term)
  AND sst.id NOT IN (SELECT id FROM backup_statistics_short_term);

-- Restore the sum field in statistics from backup_statistics
UPDATE statistics s
SET sum = b.sum
FROM backup_statistics b
WHERE s.id = b.id;

-- Restore the sum field in statistics_short_term from backup_statistics_short_term
UPDATE statistics_short_term sst
SET sum = bst.sum
FROM backup_statistics_short_term bst
WHERE sst.id = bst.id;

-- Commit the changes
COMMIT;
