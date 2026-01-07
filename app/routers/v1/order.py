from typing import Optional, List
from enum import Enum
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.schemas.request.order import OrderCreate
from app.schemas.response.order import OrderResponse, OrderDetailResponse, OrderHistoryResponse, OrderItemResponse, ProductTypeInfo, AddressInfo, PaymentInfo
from app.services.order_service import OrderService
from app.services.checkout_service import CheckoutService, PAYMENT_TIMEOUT_MINUTES
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permission import require_roles
from app.schemas.response.base import BaseResponse
from app.models.productType import ProductType

router = APIRouter()


class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    processing = "processing"
    shipping = "shipping"
    delivered = "delivered"
    completed = "completed"
    cancelled = "cancelled"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


def get_product_types_map(db: Session, product_type_ids: List[str]) -> dict:
    """Query ProductType riêng và trả về dict để lookup"""
    if not product_type_ids:
        return {}
    
    product_types = db.query(ProductType).options(
        joinedload(ProductType.product)
    ).filter(ProductType.id.in_(product_type_ids)).all()
    
    return {pt.id: pt for pt in product_types}


def build_order_items(details, pt_map: dict) -> List[dict]:
    """Build items với product info từ map"""
    items = []
    for d in details or []:
        pt = pt_map.get(d.product_type_id)
        items.append({
            "id": d.id,
            "product_type_id": d.product_type_id,
            "number": d.number,
            "price": d.price,
            "product_type": {
                "id": pt.id,
                "volume": pt.volume,
                "image_path": pt.image_path,
                "product_name": pt.product.name if pt and pt.product else None
            } if pt else None
        })
    return items


# ==================== Customer Order History ====================

@router.get("/my-orders", response_model=BaseResponse[OrderHistoryResponse])
def get_my_orders(
    status: Optional[OrderStatus] = Query(None, description="Lọc theo trạng thái đơn hàng"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sắp xếp theo thời gian"),
    skip: int = Query(0, ge=0, description="Số lượng bỏ qua"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng lấy"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lấy lịch sử đơn hàng của khách hàng đang đăng nhập.
    
    - **status**: Lọc theo trạng thái (pending, confirmed, processing, shipping, delivered, completed, cancelled)
    - **sort_order**: Sắp xếp theo thời gian (asc, desc - mặc định mới nhất trước)
    """
    service = OrderService(db)
    orders, total = service.get_user_orders(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status.value if status else None,
        sort_order=sort_order.value
    )
    
    # Collect all product_type_ids và query 1 lần
    all_pt_ids = []
    for order in orders:
        for detail in (order.details or []):
            all_pt_ids.append(detail.product_type_id)
    
    pt_map = get_product_types_map(db, all_pt_ids)
    
    # Transform orders to response format với items
    order_responses = []
    for order in orders:
        items = build_order_items(order.details, pt_map)
        order_responses.append({
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "payment_method": order.payment_method,
            "total_amount": order.total_amount,
            "discount_amount": order.discount_amount,
            "final_amount": order.final_amount,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "items": items
        })
    
    return BaseResponse(
        success=True,
        message="Lấy lịch sử đơn hàng thành công.",
        data=OrderHistoryResponse(
            items=order_responses,
            total=total,
            skip=skip,
            limit=limit
        )
    )


@router.get("/{order_id}", response_model=BaseResponse[OrderDetailResponse])
def get_order_detail(
    order_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lấy chi tiết đơn hàng.
    Khách hàng chỉ có thể xem đơn hàng của mình.
    """
    service = OrderService(db)
    
    # Kiểm tra user có role admin không
    user_roles = [r.name.lower() for r in getattr(current_user, "roles", [])]
    
    if "admin" in user_roles:
        # Admin có thể xem tất cả orders
        order = service.get_order_detail(order_id)
    else:
        # Customer chỉ xem được order của mình
        order = service.get_order_detail(order_id, user_id=current_user.id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đơn hàng."
        )
    
    # --- Xử lý hết hạn thanh toán SePay ---
    payment_expires_at = None
    remaining_seconds = None
    
    if order.status == "pending" and order.payment_method == "SEPAY":
        checkout_service = CheckoutService(db)
        if checkout_service.is_payment_expired(order):
            checkout_service.update_payment_status(order.id, "cancelled")
            # Cập nhật trạng thái cục bộ để response trả về đúng
            order.status = "cancelled"
        else:
            if order.created_at:
                payment_expires_at = order.created_at + timedelta(minutes=PAYMENT_TIMEOUT_MINUTES)
                remaining_seconds = checkout_service.get_payment_remaining_time(order)
    
    # Query ProductType để lấy thông tin product
    pt_ids = [d.product_type_id for d in (order.details or [])]
    pt_map = get_product_types_map(db, pt_ids)
    
    # Build items với product info
    items = build_order_items(order.details, pt_map)
    
    # Build address
    address_data = None
    if order.address:
        address_data = {
            "full_name": order.address.full_name,
            "phone_number": order.address.phone_number,
            "province": order.address.province,
            "district": order.address.district,
            "ward": order.address.ward,
            "detail": order.address.detail
        }
    
    # Build payment
    payment_data = None
    if order.payment:
        payment_data = {
            "id": order.payment.id,
            "method": order.payment.method,
            "status": order.payment.status,
            "amount": order.payment.amount,
            "transaction_id": order.payment.transaction_id
        }
    
    order_data = {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "payment_method": order.payment_method,
        "total_amount": order.total_amount,
        "discount_amount": order.discount_amount,
        "final_amount": order.final_amount,
        "note": order.note,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "items": items,
        "address": address_data,
        "payment": payment_data,
        "voucher_code": order.voucher.code if order.voucher else None,
        "payment_expires_at": payment_expires_at,
        "remaining_seconds": remaining_seconds
    }
    
    return BaseResponse(
        success=True,
        message="Lấy chi tiết đơn hàng thành công.",
        data=order_data
    )


# ==================== Create Order ====================

@router.post("/", response_model=BaseResponse[OrderResponse], status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Tạo đơn hàng mới.
    Yêu cầu đăng nhập.
    """
    try:
        # Override user_id với current_user để đảm bảo bảo mật
        order_in.user_id = current_user.id
        
        service = OrderService(db)
        order = service.create_order(order_in)
        return BaseResponse(success=True, message="Đặt hàng thành công.", data=order)
    except Exception as e:
        return BaseResponse(success=False, message=str(e), data=None)