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
            
            # Validate UUIDs in arrays
            # if note.quiz_ids:
                # self._validate_uuids(note.quiz_ids, "quiz_ids")
            
            # if note.flashcard_ids:
                # self._validate_uuids(note.flashcard_ids, "flashcard_ids")
            
            # if note.chat_id:
            #     self._validate_uuid(note.chat_id, "chat_id")
            
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
            
            # Validate UUIDs in arrays
            if note_update.quiz_ids is not None:
                self._validate_uuids(note_update.quiz_ids, "quiz_ids")
            
            if note_update.flashcard_ids is not None:
                self._validate_uuids(note_update.flashcard_ids, "flashcard_ids")
            
            if note_update.chat_id is not None:
                self._validate_uuid(note_update.chat_id, "chat_id")
            
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
    
    def get_chat_notes(self, chat_id: str) -> List[NoteResponse]:
        """Get all notes for a specific chat"""
        try:
            return self.dao.get_by_chat(chat_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def get_quiz_notes(self, quiz_id: str) -> List[NoteResponse]:
        """Get all notes that contain a specific quiz"""
        try:
            return self.dao.get_by_quiz(quiz_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def get_flashcard_notes(self, flashcard_id: str) -> List[NoteResponse]:
        """Get all notes that contain a specific flashcard"""
        try:
            return self.dao.get_by_flashcard(flashcard_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def _validate_uuid(self, uuid_string: str, field_name: str) -> None:
        """Validate that a string is a valid UUID"""
        try:
            import uuid
            uuid.UUID(uuid_string)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid UUID format for {field_name}")
    
    def _validate_uuids(self, uuid_list: List[str], field_name: str) -> None:
        """Validate that all strings in a list are valid UUIDs"""
        for uuid_string in uuid_list:
            self._validate_uuid(uuid_string, field_name)