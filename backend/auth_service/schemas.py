# backend/auth_service/schemas.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    token: Optional[str] = None