from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserDetailResponse(BaseModel):
    id: UUID
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    gender: Optional[int] = None
    dob: Optional[datetime] = None  
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True