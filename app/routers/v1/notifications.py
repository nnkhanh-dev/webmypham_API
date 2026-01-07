"""
Notifications Router - API thông báo cho Admin
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.permission import require_roles
from app.schemas.response.base import BaseResponse
from app.schemas.request.notification import (
    UserNotificationResponse,
    NotificationListResponse,
    UnreadCountResponse
)
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=BaseResponse[NotificationListResponse])
def get_notifications(
    skip: int = Query(0, ge=0, description="Số lượng bỏ qua"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng lấy"),
    unread_only: bool = Query(False, description="Chỉ lấy thông báo chưa đọc"),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """
    Lấy danh sách thông báo của Admin
    
    - **skip**: Số lượng bỏ qua (phân trang)
    - **limit**: Số lượng lấy tối đa
    - **unread_only**: Chỉ lấy thông báo chưa đọc
    """
    service = NotificationService(db)
    
    items, total = service.get_user_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only
    )
    
    unread_count = service.get_unread_count(current_user.id)
    
    return BaseResponse(
        success=True,
        message="Lấy danh sách thông báo thành công.",
        data=NotificationListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            unread_count=unread_count
        )
    )


@router.get("/unread-count", response_model=BaseResponse[UnreadCountResponse])
def get_unread_count(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """
    Đếm số thông báo chưa đọc của Admin
    """
    service = NotificationService(db)
    count = service.get_unread_count(current_user.id)
    
    return BaseResponse(
        success=True,
        message="Đếm thông báo chưa đọc thành công.",
        data=UnreadCountResponse(count=count)
    )


@router.put("/{notification_id}/read", response_model=BaseResponse[UserNotificationResponse])
def mark_notification_as_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """
    Đánh dấu thông báo đã đọc
    
    - **notification_id**: ID của user_notification
    """
    service = NotificationService(db)
    
    result = service.mark_as_read(notification_id, current_user.id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông báo."
        )
    
    return BaseResponse(
        success=True,
        message="Đánh dấu đã đọc thành công.",
        data=result
    )


@router.put("/read-all", response_model=BaseResponse)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """
    Đánh dấu tất cả thông báo đã đọc
    """
    service = NotificationService(db)
    count = service.mark_all_as_read(current_user.id)
    
    return BaseResponse(
        success=True,
        message=f"Đã đánh dấu {count} thông báo đã đọc.",
        data={"marked_count": count}
    )


@router.get("/{notification_id}", response_model=BaseResponse[UserNotificationResponse])
def get_notification_detail(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """
    Lấy chi tiết thông báo
    
    - **notification_id**: ID của user_notification
    """
    service = NotificationService(db)
    
    result = service.get_notification_detail(notification_id, current_user.id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông báo."
        )
    
    # Tự động đánh dấu đã đọc khi xem chi tiết
    if not result.is_read:
        service.mark_as_read(notification_id, current_user.id)
    
    return BaseResponse(
        success=True,
        message="Lấy chi tiết thông báo thành công.",
        data=result
    )
