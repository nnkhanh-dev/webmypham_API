from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class VoucherBase(BaseModel):
    # code normalized to upper-case alnum/_- between 3 and 50 chars
    code: str = Field(..., max_length=50)
    # discount as fraction (0.0 - 1.0)
    discount: float = Field(..., ge=0, le=1)
    description: Optional[str] = Field(None, max_length=255)
    quantity: int = Field(1, ge=1)
    min_order_amount: Optional[float] = Field(0, ge=0)
    max_discount: Optional[float] = Field(None, ge=0)


    @validator("code")
    def normalize_code(cls, v: str) -> str:
        v2 = v.strip()
        if not re.match(r"^[A-Za-z0-9_-]{3,50}$", v2):
            raise ValueError("code must be 3-50 characters, letters/numbers/_/- only")
        return v2.upper()

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