from typing import List, Optional
from daos.note_dao import NoteDAO
from models.models import NoteCreate, NoteUpdate, NoteResponse
from fastapi import HTTPException

class NoteService:
    """Service layer for note business logic"""
    
    def __init__(self):
        self.dao = NoteDAO()
    
    def create_note(self, note: NoteCreate) -> NoteResponse:
        """Create a new note with business logic validation"""
        try:
            # Add any business logic here (e.g., validation, formatting)
            if not note.title.strip():
                note.title = "Untitled Note"
            
            if len(note.markdown) > 100000:  # 100KB limit
                raise HTTPException(status_code=400, detail="Note content too large")
            
            return self.dao.create(note)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=400, detail=str(e))
    
    def get_note(self, note_id: str) -> NoteResponse:
        """Get a note by ID"""
        try:
            note = self.dao.get_by_id(note_id)
            if not note:
                raise HTTPException(status_code=404, detail="Note not found")
            return note
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def get_notes(self, owner_id: Optional[str] = None, is_archived: Optional[bool] = None) -> List[NoteResponse]:
        """Get notes with optional filtering"""
        try:
            return self.dao.get_all(owner_id=owner_id, is_archived=is_archived)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def update_note(self, note_id: str, note_update: NoteUpdate) -> NoteResponse:
        """Update a note with business logic validation"""
        try:
            # Add any business logic here
            if note_update.title is not None and not note_update.title.strip():
                note_update.title = "Untitled Note"
            
            if note_update.markdown is not None and len(note_update.markdown) > 100000:
                raise HTTPException(status_code=400, detail="Note content too large")
            
            updated_note = self.dao.update(note_id, note_update)
            if not updated_note:
                raise HTTPException(status_code=404, detail="Note not found")
            return updated_note
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def delete_note(self, note_id: str) -> dict:
        """Delete a note"""
        try:
            success = self.dao.delete(note_id)
            if not success:
                raise HTTPException(status_code=404, detail="Note not found")
            return {"message": "Note deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def get_user_notes(self, owner_id: str, is_archived: Optional[bool] = None) -> List[NoteResponse]:
        """Get all notes for a specific user"""
        try:
            return self.dao.get_by_owner(owner_id, is_archived)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))