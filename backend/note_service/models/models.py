from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class NoteBase(BaseModel):
    title: str
    markdown: str
    document_id: Optional[str] = None
    is_archived: bool = False

class NoteCreate(NoteBase):
    owner_id: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    markdown: Optional[str] = None
    document_id: Optional[str] = None
    is_archived: Optional[bool] = None

class NoteResponse(NoteBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True