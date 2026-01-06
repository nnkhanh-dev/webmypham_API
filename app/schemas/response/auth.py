from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str     
    token_type: str = "bearer"
    scope: Optional[str] = ""
    expires_in: int
    refresh_expires_in: int 
    
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
