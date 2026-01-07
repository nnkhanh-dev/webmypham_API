from typing import List, Optional
from pydantic import BaseModel


class CheckoutItemRequest(BaseModel):
    """Item để checkout (từ cart)"""
    cart_item_id: str
    product_type_id: str
    quantity: int


class CheckoutPreviewRequest(BaseModel):
    """Request xem trước đơn hàng"""
    items: List[CheckoutItemRequest]
    voucher_code: Optional[str] = None
    address_id: Optional[str] = None


class CreateOrderRequest(BaseModel):
    """Request tạo đơn hàng"""
    items: List[CheckoutItemRequest]
    address_id: str
    voucher_code: Optional[str] = None
    payment_method: str  # COD hoặc SEPAY
    note: Optional[str] = None


class ValidateVoucherRequest(BaseModel):
    """Request validate voucher"""
    code: str
    subtotal: float
