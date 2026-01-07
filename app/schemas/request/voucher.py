from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class VoucherBase(BaseModel):
    """Base schema cho Voucher - dùng cho Create/Update"""
    code: str = Field(..., max_length=50)
    # discount as percentage (0 - 100)
    discount: float = Field(..., ge=0, le=100)
    description: Optional[str] = Field(None, max_length=255)
    quantity: int = Field(1, ge=1)
    min_order_amount: Optional[float] = Field(0, ge=0)
    max_discount: Optional[float] = Field(None, ge=0)
    limit: Optional[int] = Field(None, ge=0)


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
    discount: Optional[float] = Field(None, ge=0, le=100)
    description: Optional[str] = Field(None, max_length=255)
    quantity: Optional[int] = Field(None, ge=0)
    min_order_amount: Optional[float] = Field(None, ge=0)
    max_discount: Optional[float] = Field(None, ge=0)
    limit: Optional[int] = Field(None, ge=0)

class VoucherInDBBase(BaseModel):
    id: str  # UUID string
    code: str
    discount: float
    description: Optional[str] = None
    quantity: int
    min_order_amount: Optional[float] = None
    max_discount: Optional[float] = None
    limit: Optional[int] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VoucherResponse(VoucherInDBBase):
    pass
