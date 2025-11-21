-- Migration: Add Styling Columns to Notes Table

-- Add styling columns to store editor formatting preferences
ALTER TABLE note ADD COLUMN IF NOT EXISTS font_size TEXT DEFAULT '16px';
ALTER TABLE note ADD COLUMN IF NOT EXISTS font_family TEXT DEFAULT 'Inter, -apple-system, BlinkMacSystemFont, ''Segoe UI'', Roboto, ''Helvetica Neue'', sans-serif';
ALTER TABLE note ADD COLUMN IF NOT EXISTS line_height TEXT DEFAULT '1.65';

