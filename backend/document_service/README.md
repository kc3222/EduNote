# Document Service

A microservice for managing document uploads and storage with CRUD operations.

## Features

- File upload with drag-and-drop support
- Support for PDF, Word, Text, and Markdown files
- File storage on disk with database metadata
- PDF viewing capabilities
- Document management (CRUD operations)

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the service:**
   ```bash
   python main.py --port 8002
   ```

3. **Service runs on:** `http://localhost:8002`

## API Endpoints

- `GET /` - Service status
- `GET /health` - Health check
- `POST /documents/upload` - Upload document
- `GET /documents` - List documents (with optional owner_id filter)
- `GET /documents/{id}` - Get specific document metadata
- `GET /documents/{id}/download` - Download document file
- `GET /documents/{id}/view` - View document in browser (for PDFs)
- `PUT /documents/{id}` - Update document metadata
- `DELETE /documents/{id}` - Delete document and file

## File Storage

- Files are stored in the `uploads/` directory
- Filenames are UUID-based to prevent conflicts
- File metadata is stored in PostgreSQL database
- Maximum file size: 50MB per file

## Supported File Types

- PDF: `application/pdf`
- Text: `text/plain`
- Word: `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Markdown: `text/markdown`

## Environment Variables

- `DB_HOST` (default: localhost)
- `DB_PORT` (default: 5432)
- `DB_NAME` (default: app_db)
- `DB_USER` (default: app_user)
- `DB_PASSWORD` (default: app_pass)

## Integration

The document service integrates with the frontend via:
- Upload modal component
- PDF viewer component
- Document selection dropdown
- Vite proxy configuration routing `/documents/*` to port 8002
