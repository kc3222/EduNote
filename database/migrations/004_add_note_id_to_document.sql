-- Migration: Add note_id to Document Table

-- Add note_id column to link documents to notes
ALTER TABLE document ADD COLUMN IF NOT EXISTS note_id UUID REFERENCES note(id) ON DELETE CASCADE;

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_document_note_id ON document(note_id) WHERE note_id IS NOT NULL;

-- Add comment to document the relationship
COMMENT ON COLUMN document.note_id IS 'Links document to a specific note. Each note can have one document.';

