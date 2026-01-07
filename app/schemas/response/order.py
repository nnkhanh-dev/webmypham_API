from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class ProductTypeInfo(BaseModel):
    """Thông tin ProductType kèm trong OrderDetail"""
    id: str
    volume: Optional[str] = None
    image_path: Optional[str] = None
    product_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class OrderItemResponse(BaseModel):
    """Chi tiết đơn hàng"""
    id: str
    product_type_id: str
    quantity: Optional[int] = None
    number: Optional[int] = None  # alias for quantity in DB
    price: Optional[float] = None
    product_type: Optional[ProductTypeInfo] = None

    class Config:
        from_attributes = True


class PaymentInfo(BaseModel):
    """Thông tin thanh toán"""
    id: str
    method: Optional[str] = None
    status: Optional[str] = None
    amount: Optional[float] = None
    transaction_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Response cho một đơn hàng"""
    id: str
    user_id: str
    status: str
    total_amount: float
    discount_amount: Optional[float] = None
    final_amount: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderDetailResponse(BaseModel):
    """Response chi tiết đơn hàng kèm items và payment"""
    id: str
    user_id: str
    status: str
    total_amount: float
    discount_amount: Optional[float] = None
    final_amount: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    payment: Optional[PaymentInfo] = None

    class Config:
        from_attributes = True


class OrderHistoryResponse(BaseModel):
    """Response cho danh sách lịch sử đơn hàng với phân trang"""
    items: List[OrderResponse]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True