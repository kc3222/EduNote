-- Migration: Initial Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable CITEXT extension for case-insensitive text
CREATE EXTENSION IF NOT EXISTS "citext";

-- Users table
CREATE TABLE app_user (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         CITEXT UNIQUE NOT NULL,
  display_name  TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Notes table
CREATE TABLE note (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id       UUID NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
  document_id    UUID,                             -- optional grouping link
  title          TEXT NOT NULL DEFAULT '',
  markdown       TEXT NOT NULL,                    -- Milkdown source
  quiz_ids       UUID[] DEFAULT '{}',              -- optional list of quizzes
  flashcard_ids  UUID[] DEFAULT '{}',              -- optional list of flashcards
  chat_id        UUID,                             -- optional chat link
  is_archived    BOOLEAN NOT NULL DEFAULT FALSE,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_note_owner_id ON note(owner_id);
CREATE INDEX idx_note_document_id ON note(document_id) WHERE document_id IS NOT NULL;
CREATE INDEX idx_note_created_at ON note(created_at);
CREATE INDEX idx_note_updated_at ON note(updated_at);
CREATE INDEX idx_note_is_archived ON note(is_archived);
CREATE INDEX idx_note_chat_id ON note(chat_id) WHERE chat_id IS NOT NULL;

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