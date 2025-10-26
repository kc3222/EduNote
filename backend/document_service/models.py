from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

class DocumentCreate(BaseModel):
    title: str
    filename: str
    file_path: str
    file_size: int
    content_type: str
    owner_id: str
    description: Optional[str] = None

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    title: str
    filename: str
    file_size: int
    content_type: str
    owner_id: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
