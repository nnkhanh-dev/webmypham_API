from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CartItemBase(BaseModel):
    product_type_id: str = Field(...)
    quantity: int = Field(..., ge=1)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    product_type_id: Optional[str] = Field(None, description="ID của biến thể sản phẩm mới (thay đổi màu sắc, dung tích...)")


class CartItemInDBBase(CartItemBase):
    id: str
    cart_id: str
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class CartItemResponse(CartItemInDBBase):
    pass


class CartBase(BaseModel):
    pass


class CartCreate(CartBase):
    pass


class CartInDBBase(CartBase):
    id: str
    user_id: str
    items: Optional[List[CartItemResponse]] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class CartResponse(CartInDBBase):
    pass
