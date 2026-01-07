from typing import Optional
from enum import Enum
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.request.order import OrderCreate
from app.schemas.response.order import OrderResponse, OrderDetailResponse, OrderHistoryResponse
from app.services.order_service import OrderService
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permission import require_roles
from app.schemas.response.base import BaseResponse

router = APIRouter()


class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipping = "shipping"
    delivered = "delivered"
    cancelled = "cancelled"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


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
    
    - **status**: Lọc theo trạng thái (pending, confirmed, shipping, delivered, cancelled)
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
    
    return BaseResponse(
        success=True,
        message="Lấy lịch sử đơn hàng thành công.",
        data=OrderHistoryResponse(
            items=orders,
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
    
    # Map details to items for response
    order_data = {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "discount_amount": order.discount_amount,
        "final_amount": order.final_amount,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "items": order.details if order.details else [],
        "payment": order.payment
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