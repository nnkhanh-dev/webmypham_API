from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NotificationBase(BaseModel):
    """Base schema cho Notification"""
    title: str = Field(..., max_length=200, description="Tiêu đề thông báo")
    content: str = Field(..., description="Nội dung thông báo")
    type: str = Field("system", max_length=50, description="Loại: order, system, promotion")


class NotificationCreate(NotificationBase):
    """Schema tạo notification"""
    order_id: Optional[str] = Field(None, description="ID đơn hàng (nếu type=order)")
    user_ids: Optional[List[str]] = Field(None, description="Danh sách user IDs để gửi")
    is_global: bool = Field(False, description="Gửi đến tất cả users")


class NotificationInfo(BaseModel):
    """Thông tin notification"""
    id: str
    title: str
    content: str
    type: str
    order_id: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserNotificationResponse(BaseModel):
    """Response cho user notification"""
    id: str
    user_id: str
    notification_id: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    notification: Optional[NotificationInfo] = None
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Paginated response cho danh sách notifications"""
    items: List[UserNotificationResponse]
    total: int
    skip: int
    limit: int
    unread_count: int
    
    class Config:
        from_attributes = True


class UnreadCountResponse(BaseModel):
    """Response cho đếm unread"""
    count: int
