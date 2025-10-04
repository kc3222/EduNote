from fastapi import FastAPI, HTTPException, Depends, Request
from typing import List, Optional
from services.note_service import NoteService
from models.models import NoteCreate, NoteUpdate, NoteResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os
import argparse
import json

app = FastAPI(title="Notes Service", version="1.0.0")

# Initialize service
note_service = NoteService()

FRONTEND_ORIGIN = "http://localhost:5173"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Notes Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/notes", response_model=NoteResponse)
async def create_note(request: Request):
    """Create a new note"""
    try:
        # Get raw body for debugging
        body = await request.body()
        
        # Parse JSON manually to see what we get
        note_data = json.loads(body)
        
        # Try to create NoteCreate object
        note = NoteCreate(**note_data)
        
        return note_service.create_note(note)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    # print(f"Creating note: {note}")
    # return note_service.create_note(note)

@app.get("/notes", response_model=List[NoteResponse])
async def get_notes(owner_id: Optional[str] = None, is_archived: Optional[bool] = None):
    """Get notes with optional filtering"""
    res = note_service.get_notes(owner_id=owner_id, is_archived=is_archived)
    return res

@app.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str):
    """Get a specific note by ID"""
    return note_service.get_note(note_id)

@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, note_update: NoteUpdate):
    """Update a note"""
    return note_service.update_note(note_id, note_update)

@app.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete a note"""
    return note_service.delete_note(note_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Notes Service")
    parser.add_argument("--port", type=int, default=8001, help="Port number to run the service on")
    args = parser.parse_args()
    
    print(f"Starting Notes Service on port {args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)