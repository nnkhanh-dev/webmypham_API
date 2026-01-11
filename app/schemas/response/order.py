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
    number: Optional[int] = None
    price: Optional[float] = None
    product_type: Optional[ProductTypeInfo] = None

    class Config:
        from_attributes = True


class AddressInfo(BaseModel):
    """Thông tin địa chỉ giao hàng"""
    full_name: str
    phone_number: str
    province: str
    district: str
    ward: str
    detail: str
    
    class Config:
        from_attributes = True


class PaymentInfo(BaseModel):
    """Thông tin thanh toán"""
    id: str
    method: Optional[str] = None
    status: Optional[str] = None
    amount: Optional[float] = None
    transaction_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Response cho một đơn hàng (list view)"""
    id: str
    user_id: str
    user_name: Optional[str] = None
    status: str
    payment_method: Optional[str] = None
    total_amount: float
    discount_amount: Optional[float] = None
    final_amount: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderDetailResponse(BaseModel):
    """Response chi tiết đơn hàng kèm items, address và payment"""
    id: str
    user_id: str
    status: str
    payment_method: Optional[str] = None
    total_amount: float
    discount_amount: Optional[float] = None
    final_amount: float
    note: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    address: Optional[AddressInfo] = None
    payment: Optional[PaymentInfo] = None
    voucher_code: Optional[str] = None
    payment_expires_at: Optional[datetime] = None
    remaining_seconds: Optional[int] = None

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