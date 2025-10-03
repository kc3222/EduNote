-- EduNote Database Schema
-- This file initializes the database with the required tables

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE app_user (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         TEXT UNIQUE NOT NULL,
  password      TEXT NOT NULL,
  display_name  TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Notes table
CREATE TABLE note (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id      UUID NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
  document_id   UUID,                             -- optional link to a "document" (nullable)
  title         TEXT NOT NULL DEFAULT '',
  markdown      TEXT NOT NULL,                    -- Milkdown source
  quiz_ids      TEXT[] DEFAULT '{}',              -- Array of quiz UUIDs
  flashcard_ids TEXT[] DEFAULT '{}',              -- Array of flashcard UUIDs
  chat_id       UUID,                             -- Chat UUID (nullable)
  is_archived   BOOLEAN NOT NULL DEFAULT FALSE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- If you want to enforce "document_id" references later, you could add:
--   REFERENCES document(id)
-- But for now we keep it flexible & nullable.

-- Create indexes for better performance
CREATE INDEX idx_note_owner_id ON note(owner_id);
CREATE INDEX idx_note_document_id ON note(document_id) WHERE document_id IS NOT NULL;
CREATE INDEX idx_note_chat_id ON note(chat_id) WHERE chat_id IS NOT NULL;
CREATE INDEX idx_note_created_at ON note(created_at);
CREATE INDEX idx_note_updated_at ON note(updated_at);
CREATE INDEX idx_note_is_archived ON note(is_archived);
-- GIN indexes for array fields for efficient array operations
CREATE INDEX idx_note_quiz_ids ON note USING GIN(quiz_ids);
CREATE INDEX idx_note_flashcard_ids ON note USING GIN(flashcard_ids);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at on note updates
CREATE TRIGGER update_note_updated_at 
    BEFORE UPDATE ON note 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default test user
INSERT INTO app_user (id, email, display_name, password) 
VALUES (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'demo@user.com',
    'Test User',
    'password123'
) ON CONFLICT (email) DO NOTHING;