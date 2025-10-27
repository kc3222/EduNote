-- Migration: Add Summary Columns to Notes Table

-- Add summary_json column to store AI-generated summary
ALTER TABLE note ADD COLUMN IF NOT EXISTS summary_json JSONB;

-- Add summary_updated_at column to track when summary was last generated
ALTER TABLE note ADD COLUMN IF NOT EXISTS summary_updated_at TIMESTAMPTZ;

-- Create index on summary_updated_at for efficient queries
CREATE INDEX IF NOT EXISTS idx_note_summary_updated_at ON note(summary_updated_at);

