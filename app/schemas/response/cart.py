from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- Nested Schemas for Cart Response ---

class TypeValueInCart(BaseModel):
    """TypeValue info trong cart (màu sắc, dung tích...)"""
    id: str
    name: str

    class Config:
        orm_mode = True


class ProductInCart(BaseModel):
    """Product info trong cart"""
    id: str
    name: str
    thumbnail: Optional[str] = None

    class Config:
        orm_mode = True


class ProductTypeInCart(BaseModel):
    """ProductType (biến thể) info trong cart"""
    id: str
    price: Optional[float] = None
    discount_price: Optional[float] = None
    stock: Optional[int] = None
    image_path: Optional[str] = None
    volume: Optional[str] = None
    skin_type: Optional[str] = None
    origin: Optional[str] = None
    product: Optional[ProductInCart] = None
    type_value: Optional[TypeValueInCart] = None

    class Config:
        orm_mode = True


class CartItemFullResponse(BaseModel):
    """CartItem với đầy đủ thông tin sản phẩm"""
    id: str
    cart_id: str
    product_type_id: str
    quantity: int
    product_type: Optional[ProductTypeInCart] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class CartFullResponse(BaseModel):
    """Cart với đầy đủ thông tin items"""
    id: str
    user_id: str
    items: Optional[list[CartItemFullResponse]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
