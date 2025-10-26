from fastapi import FastAPI, HTTPException, Depends, Request
from note_service.services.note_service import NoteService
from note_service.services.summarize_service import SummarizeService
from note_service.models.models import NoteCreate, NoteUpdate, NoteResponse

from typing import List, Optional
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os
import argparse
import json

app = FastAPI(title="Notes Service", version="1.0.0")

note_service = NoteService()
summarize_service = SummarizeService()  # share DAO

FRONTEND_ORIGIN = "http://localhost:5173"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------
# Basic health endpoints
# --------------------------------------------------------------------

@app.get("/")
async def root():
    return {"message": "Notes Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# --------------------------------------------------------------------
# CRUD for notes
# --------------------------------------------------------------------

@app.post("/notes", response_model=NoteResponse)
async def create_note(request: Request):
    """Create a new note"""
    try:
        body = await request.body()
        note_data = json.loads(body)
        note = NoteCreate(**note_data)
        return note_service.create_note(note)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.get("/notes", response_model=List[NoteResponse])
async def get_notes(owner_id: Optional[str] = None, is_archived: Optional[bool] = None):
    """Get notes with optional filtering"""
    return note_service.get_notes(owner_id=owner_id, is_archived=is_archived)

@app.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str):
    """Get a specific note by ID"""
    note = note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, note_update: NoteUpdate):
    """Update a note"""
    return note_service.update_note(note_id, note_update)

@app.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete a note"""
    return note_service.delete_note(note_id)

# --------------------------------------------------------------------
# Summarization endpoints
# --------------------------------------------------------------------

@app.post("/notes/{note_id}/summarize")
def summarize_note_endpoint(note_id: str):
    """
    Return a structured summary (JSON only, not persisted).
    """
    note = note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    summary = summarize_service.summarize_note(note)
    return summary


@app.put("/notes/{note_id}/summary")
def summarize_and_persist(note_id: str):
    """
    Compute a Gemini summary and persist it to summary_json + summary_updated_at.
    Matches the frontend PUT /notes/{id}/summary call.
    """
    note = note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    summary = summarize_service.summarize_and_persist(note_id)
    return {"note_id": note_id, "summary": summary}


@app.get("/notes/{note_id}/summary")
def get_persisted_summary(note_id: str):
    """
    Retrieve the stored summary (without recomputing).
    """
    note = note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {
        "note_id": note_id,
        "summary": note.summary_json,
        "summary_updated_at": note.summary_updated_at,
    }

# --------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Notes Service")
    parser.add_argument("--port", type=int, default=8001, help="Port number to run the service on")
    args = parser.parse_args()

    print(f"Starting Notes Service on port {args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)