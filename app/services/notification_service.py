from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.repositories.notification_repository import NotificationRepository
from app.models.notification import Notification
from app.models.userNotification import UserNotification
from app.models.role import Role
from app.models.userRole import UserRole
from app.models.user import User


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = NotificationRepository(db)
    
    def create_order_notification(
        self,
        order_id: str,
        customer_name: str,
        total_amount: float,
        created_by: Optional[str] = None
    ) -> Notification:
        """
        Tạo thông báo đơn hàng mới và gửi đến tất cả admin
        """
        title = "🛒 Đơn hàng mới"
        content = f"Khách hàng {customer_name} vừa đặt đơn hàng trị giá {total_amount:,.0f}đ"
        
        notification = self.repo.create_notification(
            title=title,
            content=content,
            type="order",
            order_id=order_id,
            sender_id=created_by,
            is_global=False,
            created_by=created_by
        )
        
        # Gửi notification đến tất cả admin
        self._notify_admins(notification.id)
        
        return notification
    
    def _notify_admins(self, notification_id: str) -> int:
        """Gửi notification đến tất cả users có role ADMIN"""
        # Lấy tất cả admin users
        admin_role = self.db.query(Role).filter(
            Role.name.ilike("admin"),
            Role.deleted_at.is_(None)
        ).first()
        
        if not admin_role:
            return 0
        
        admin_users = self.db.query(User).join(
            UserRole, User.id == UserRole.user_id
        ).filter(
            UserRole.role_id == admin_role.id,
            User.deleted_at.is_(None)
        ).all()
        
        count = 0
        for user in admin_users:
            self.repo.create_user_notification(
                user_id=user.id,
                notification_id=notification_id
            )
            count += 1
        
        return count
    
    def get_user_notifications(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False
    ) -> Tuple[List[UserNotification], int]:
        """Lấy danh sách notifications của user"""
        return self.repo.get_user_notifications(
            user_id=user_id,
            skip=skip,
            limit=limit,
            unread_only=unread_only
        )
    
    def get_unread_count(self, user_id: str) -> int:
        """Đếm số notification chưa đọc"""
        return self.repo.get_unread_count(user_id)
    
    def mark_as_read(self, user_notification_id: str, user_id: str) -> Optional[UserNotification]:
        """Đánh dấu notification đã đọc"""
        return self.repo.mark_as_read(user_notification_id, user_id)
    
    def mark_all_as_read(self, user_id: str) -> int:
        """Đánh dấu tất cả notifications đã đọc"""
        return self.repo.mark_all_as_read(user_id)
    
    def get_notification_detail(
        self, 
        user_notification_id: str, 
        user_id: str
    ) -> Optional[UserNotification]:
        """Lấy chi tiết notification"""
        return self.repo.get_user_notification_by_id(user_notification_id, user_id)


def notify_admins_new_order(
    db: Session,
    order_id: str,
    customer_name: str,
    total_amount: float,
    created_by: Optional[str] = None
) -> Notification:
    """Helper function để gọi từ order service"""
    service = NotificationService(db)
    return service.create_order_notification(
        order_id=order_id,
        customer_name=customer_name,
        total_amount=total_amount,
        created_by=created_by
    )
