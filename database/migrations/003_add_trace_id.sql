-- Migration 003: Add trace_id column to crops table
-- Execute commands one by one - column must exist before constraint/index

-- Step 1: Add trace_id column (will fail silently if already exists - handled by migration system)
ALTER TABLE crops ADD COLUMN trace_id VARCHAR(20);

-- Step 2: Add unique constraint (will fail if column doesn't exist or constraint already exists)
ALTER TABLE crops ADD UNIQUE (trace_id);

-- Step 3: Create index on trace_id (will fail if column doesn't exist or index already exists)
CREATE INDEX idx_trace_id ON crops(trace_id);

