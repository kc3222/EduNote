-- Migration: Add Document Table

-- Documents table for file storage
CREATE TABLE document (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title          TEXT NOT NULL,
    filename       TEXT NOT NULL,
    file_path      TEXT NOT NULL,
    file_size      INTEGER NOT NULL,
    content_type   TEXT NOT NULL,
    owner_id       UUID NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    description    TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for better performance
CREATE INDEX idx_document_owner_id ON document(owner_id);
CREATE INDEX idx_document_created_at ON document(created_at);
CREATE INDEX idx_document_content_type ON document(content_type);

-- Auto-update trigger for updated_at
CREATE TRIGGER update_document_updated_at 
    BEFORE UPDATE ON document 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
