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
    
    # --- Xử lý hết hạn thanh toán SePay (Lazy check - không cần cronjob) ---
    payment_expires_at = None
    remaining_seconds = None
    
    if order.status == "pending" and order.payment_method == "SEPAY":
        checkout_service = CheckoutService(db)
        
        # Check if payment has expired and auto-cancel if needed
        if checkout_service.is_payment_expired(order):
            # Update payment status
            if order.payment:
                order.payment.status = "cancelled"
            
            # Update order status to cancelled
            order.status = "cancelled"
            
            # Restore stock
            checkout_service._restore_stock(order)
            
            # Commit changes
            db.commit()
            db.refresh(order)
        else:
            # Payment still valid, calculate remaining time
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
            "transaction_id": order.payment.transaction_id,
            "created_at": order.payment.created_at,
            "updated_at": order.payment.updated_at
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
        
        # Tạo thông báo cho admin về đơn hàng mới
        try:
            from app.services.notification_service import notify_admins_new_order
            customer_name = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email
            notify_admins_new_order(
                db=db,
                order_id=str(order.id),
                customer_name=customer_name,
                total_amount=order.final_amount,
                created_by=str(current_user.id)
            )
            print(f"✅ Notification created for order {order.id}")
        except Exception as notif_error:
            # Log lỗi nhưng không fail order creation
            print(f"❌ Error creating notification: {notif_error}")
            import traceback
            traceback.print_exc()
        
        return BaseResponse(success=True, message="Đặt hàng thành công.", data=order)
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        import traceback
        traceback.print_exc()
        return BaseResponse(success=False, message=str(e), data=None)


# ==================== Admin Order Management ====================

@router.patch("/{order_id}/status", response_model=BaseResponse[OrderDetailResponse])
def update_order_status(
    order_id: str,
    new_status: OrderStatus = Query(..., description="Trạng thái mới"),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """
    Cập nhật trạng thái đơn hàng (Admin only)
    
    - **new_status**: pending, confirmed, processing, shipping, delivered, completed, cancelled
    """
    from app.models.order import Order
    from app.services.order_state_machine import validate_transition, requires_payment_confirmation
    
    # Lấy đơn hàng với payment info
    order = db.query(Order).options(
        joinedload(Order.payment)
    ).filter(Order.id == order_id, Order.deleted_at.is_(None)).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đơn hàng."
        )
    
    # Check if payment confirmation is required (for SePay orders)
    blocked, error_msg = requires_payment_confirmation(order, new_status.value)
    if blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Validate state transition
    error_msg = validate_transition(order.status, new_status.value)
    if error_msg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Cập nhật trạng thái
    order.status = new_status.value
    order.updated_at = datetime.now()
    db.commit()
    db.refresh(order)
    
    # Tạo thông báo cho khách hàng về thay đổi trạng thái
    from app.services.notification_service import notify_user_order_status_change
    notify_user_order_status_change(
        db=db,
        order_id=str(order.id),
        user_id=str(order.user_id),
        new_status=new_status.value,
        updated_by=str(current_user.id)
    )
    
    # Trả về chi tiết đơn hàng đã cập nhật
    service = OrderService(db)
    updated_order = service.get_order_detail(order_id)
    
    # Query ProductType để lấy thông tin product
    pt_ids = [d.product_type_id for d in (updated_order.details or [])]
    pt_map = get_product_types_map(db, pt_ids)
    
    # Build items với product info
    items = build_order_items(updated_order.details, pt_map)
    
    # Build address
    address_data = None
    if updated_order.address:
        address_data = {
            "full_name": updated_order.address.full_name,
            "phone_number": updated_order.address.phone_number,
            "province": updated_order.address.province,
            "district": updated_order.address.district,
            "ward": updated_order.address.ward,
            "detail": updated_order.address.detail
        }
    
    # Build payment
    payment_data = None
    if updated_order.payment:
        payment_data = {
            "id": updated_order.payment.id,
            "method": updated_order.payment.method,
            "status": updated_order.payment.status,
            "amount": updated_order.payment.amount,
            "transaction_id": updated_order.payment.transaction_id,
            "created_at": updated_order.payment.created_at,
            "updated_at": updated_order.payment.updated_at
        }
    
    order_data = {
        "id": updated_order.id,
        "user_id": updated_order.user_id,
        "status": updated_order.status,
        "payment_method": updated_order.payment_method,
        "total_amount": updated_order.total_amount,
        "discount_amount": updated_order.discount_amount,
        "final_amount": updated_order.final_amount,
        "note": updated_order.note,
        "created_at": updated_order.created_at,
        "updated_at": updated_order.updated_at,
        "items": items,
        "address": address_data,
        "payment": payment_data,
        "voucher_code": updated_order.voucher.code if updated_order.voucher else None
    }
    
    return BaseResponse(
        success=True,
        message=f"Cập nhật trạng thái đơn hàng thành công: {new_status.value}",
        data=order_data
    )


@router.get("/admin/all", response_model=BaseResponse[OrderHistoryResponse])
def get_all_orders_admin(
    status: Optional[OrderStatus] = Query(None, description="Lọc theo trạng thái"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sắp xếp theo thời gian"),
    skip: int = Query(0, ge=0, description="Số lượng bỏ qua"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng lấy"),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """
    Lấy tất cả đơn hàng (Admin only)
    """
    from app.models.order import Order
    from app.models.user import User
    from sqlalchemy.orm import joinedload
    
    query = db.query(Order).options(
        joinedload(Order.user)
    ).filter(Order.deleted_at.is_(None))
    
    if status:
        query = query.filter(Order.status == status.value)
    
    # Count total
    total = query.count()
    
    # Sort and paginate
    if sort_order.value == "desc":
        query = query.order_by(Order.created_at.desc())
    else:
        query = query.order_by(Order.created_at.asc())
    
    orders = query.offset(skip).limit(limit).all()
    
    # Collect all product_type_ids
    all_pt_ids = []
    for order in orders:
        for detail in (order.details or []):
            all_pt_ids.append(detail.product_type_id)
    
    pt_map = get_product_types_map(db, all_pt_ids)
    
    # Transform orders with user info
    order_responses = []
    for order in orders:
        items = build_order_items(order.details, pt_map)
        
        # Get user full name
        user_name = "Khách hàng"
        if order.user:
            first_name = order.user.first_name or ""
            last_name = order.user.last_name or ""
            user_name = f"{first_name} {last_name}".strip() or order.user.email
            print(f"📦 Order {order.id[:8]}: User = {user_name}")
        else:
            print(f"📦 Order {order.id[:8]}: NO USER LOADED")
        
        order_responses.append({
            "id": order.id,
            "user_id": order.user_id,
            "user_name": user_name,
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
        message="Lấy danh sách đơn hàng thành công.",
        data=OrderHistoryResponse(
            items=order_responses,
            total=total,
            skip=skip,
            limit=limit
        )
    )
