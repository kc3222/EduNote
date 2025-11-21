from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class NoteBase(BaseModel):
    title: str
    markdown: str
    document_id: Optional[str] = None
    quiz_ids: List[str] = []  # List of quiz UUIDs
    flashcard_ids: List[str] = []  # List of flashcard UUIDs
    chat_id: Optional[str] = None  # Chat UUID
    is_archived: bool = False
    font_size: Optional[str] = None
    font_family: Optional[str] = None
    line_height: Optional[str] = None

class NoteCreate(NoteBase):
    owner_id: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    markdown: Optional[str] = None
    document_id: Optional[str] = None
    quiz_ids: Optional[List[str]] = None
    flashcard_ids: Optional[List[str]] = None
    chat_id: Optional[str] = None
    is_archived: Optional[bool] = None
    font_size: Optional[str] = None
    font_family: Optional[str] = None
    line_height: Optional[str] = None

class NoteResponse(BaseModel):
    id: str
    owner_id: str
    title: str
    markdown: Optional[str] = None
    document_id: Optional[str] = None
    quiz_ids: List[str] = []
    flashcard_ids: List[str] = []
    chat_id: Optional[str] = None
    is_archived: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    summary_json: Optional[dict] = None
    summary_updated_at: Optional[datetime] = None
    font_size: Optional[str] = None
    font_family: Optional[str] = None
    line_height: Optional[str] = None