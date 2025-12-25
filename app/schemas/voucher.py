from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VoucherBase(BaseModel):
    code: str = Field(..., max_length=50)
    discount: float = Field(..., ge=0)
    description: Optional[str] = Field(None, max_length=255)
    quantity: int = Field(1, ge=0)

class VoucherCreate(VoucherBase):
    pass

class VoucherUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    discount: Optional[float] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=255)
    quantity: Optional[int] = Field(None, ge=0)

class VoucherInDBBase(VoucherBase):
    id: int
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class VoucherResponse(VoucherInDBBase):
    pass