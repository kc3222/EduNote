-- Migration: Initial Schema
-- Created: 2024-01-01T00:00:00

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE app_user (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         TEXT UNIQUE NOT NULL,
  display_name  TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Notes table
CREATE TABLE note (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id     UUID NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
  document_id  UUID,
  title        TEXT NOT NULL DEFAULT '',
  markdown     TEXT NOT NULL,
  is_archived  BOOLEAN NOT NULL DEFAULT FALSE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_note_owner_id ON note(owner_id);
CREATE INDEX idx_note_document_id ON note(document_id) WHERE document_id IS NOT NULL;
CREATE INDEX idx_note_created_at ON note(created_at);
CREATE INDEX idx_note_updated_at ON note(updated_at);
CREATE INDEX idx_note_is_archived ON note(is_archived);

-- Auto-update trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_note_updated_at 
    BEFORE UPDATE ON note 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();