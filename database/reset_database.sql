-- Reset Database Script
-- This script clears all data from blocks, transactions, and crops tables
-- While keeping users and schema intact

-- Disable foreign key checks temporarily
SET FOREIGN_KEY_CHECKS = 0;

-- Clear blocks table
DELETE FROM blocks;
ALTER TABLE blocks AUTO_INCREMENT = 1;

-- Clear transactions table
DELETE FROM transactions;
ALTER TABLE transactions AUTO_INCREMENT = 1;

-- Clear crops table
DELETE FROM crops;
ALTER TABLE crops AUTO_INCREMENT = 1;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Verify tables are empty
SELECT 'blocks' as table_name, COUNT(*) as row_count FROM blocks
UNION ALL
SELECT 'transactions' as table_name, COUNT(*) as row_count FROM transactions
UNION ALL
SELECT 'crops' as table_name, COUNT(*) as row_count FROM crops;

-- Output confirmation
SELECT '✓ Database reset complete' as status;
