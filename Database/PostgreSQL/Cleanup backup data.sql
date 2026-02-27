-- PostgreSQL: Cleanup the backup data after the import script has been executed

-- Start a transaction so that we can rollback any changes if needed
BEGIN;

-- Drop the backup tables
DROP TABLE IF EXISTS backup_statistics;
DROP TABLE IF EXISTS backup_statistics_short_term;

-- Commit the changes
COMMIT;
