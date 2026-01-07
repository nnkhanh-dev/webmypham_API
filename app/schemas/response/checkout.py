from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class CheckoutItemResponse(BaseModel):
    """Item trong checkout preview"""
    cart_item_id: str
    product_type_id: str
    product_name: str
    variant_name: Optional[str] = None
    image: Optional[str] = None
    quantity: int
    price: float
    discount_price: Optional[float] = None
    line_total: float


class VoucherAppliedResponse(BaseModel):
    """Thông tin voucher đã áp dụng"""
    code: str
    discount_amount: float
    description: Optional[str] = None


class CheckoutPreviewResponse(BaseModel):
    """Response xem trước đơn hàng"""
    items: List[CheckoutItemResponse]
    subtotal: float  # Tổng tiền gốc
    discount: float  # Giảm giá từ voucher
    shipping_fee: float  # Phí ship (0 = miễn phí)
    total: float  # Tổng cuối cùng
    voucher: Optional[VoucherAppliedResponse] = None
    address_id: Optional[str] = None


class ValidateVoucherResponse(BaseModel):
    """Response validate voucher"""
    valid: bool
    discount_amount: float = 0
    message: str


class CreateOrderResponse(BaseModel):
    """Response tạo đơn hàng"""
    order_id: str
    status: str
    payment_method: str
    total_amount: float
    discount_amount: float
    final_amount: float
    payment_url: Optional[str] = None  # URL thanh toán SePay (nếu có)
    payment_content: Optional[str] = None # Nội dung chuyển khoản
    created_at: datetime


class PaymentStatusResponse(BaseModel):
    """Response trạng thái thanh toán"""
    order_id: str
    payment_status: str
    order_status: str
    transaction_id: Optional[str] = None
