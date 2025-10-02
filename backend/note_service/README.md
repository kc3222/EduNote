# Notes Service

A microservice for managing notes with CRUD operations.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the service:**
   ```bash
   python main.py
   ```

3. **Service runs on:** `http://localhost:8001`

## API Endpoints

- `GET /` - Service status
- `GET /health` - Health check
- `POST /notes` - Create note
- `GET /notes` - List notes (with optional filters)
- `GET /notes/{id}` - Get specific note
- `PUT /notes/{id}` - Update note
- `DELETE /notes/{id}` - Delete note

## Environment Variables

- `DB_HOST` (default: localhost)
- `DB_PORT` (default: 5432)
- `DB_NAME` (default: app_db)
- `DB_USER` (default: app_user)
- `DB_PASSWORD` (default: app_pass)