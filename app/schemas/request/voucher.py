from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class VoucherBase(BaseModel):
    """Base schema cho Voucher - dùng cho Create/Update"""
    code: str = Field(..., max_length=50)
    # discount có thể là:
    # - Phần trăm: 0.0-1.0 (0.1 = 10%) hoặc 1-100 (10 = 10%)
    # - Số tiền cố định: 5000 = giảm 5000đ
    # Tùy thuộc vào cách bạn muốn xử lý
    discount: float = Field(..., ge=0)  # Bỏ le=1 để linh hoạt
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
    discount: Optional[float] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=255)
    quantity: Optional[int] = Field(None, ge=0)
    min_order_amount: Optional[float] = Field(None, ge=0)
    max_discount: Optional[float] = Field(None, ge=0)
    limit: Optional[int] = Field(None, ge=0)

    @validator("code")
    def normalize_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v2 = v.strip()
        if not re.match(r"^[A-Za-z0-9_-]{3,50}$", v2):
            raise ValueError("code must be 3-50 characters, letters/numbers/_/- only")
        return v2.upper()


class VoucherInDBBase(BaseModel):
    """Schema cho response - không validate giá trị, chỉ map từ DB"""
    id: str
    code: str
    discount: float  # Không có constraint
    description: Optional[str] = None
    quantity: int
    min_order_amount: Optional[float] = None
    max_discount: Optional[float] = None
    limit: Optional[int] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class VoucherResponse(VoucherInDBBase):
    pass