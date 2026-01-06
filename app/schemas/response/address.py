from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AddressResponse(BaseModel):
    id: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    ward: Optional[str] = None
    detail: Optional[str] = None
    is_default: bool = False
    user_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

