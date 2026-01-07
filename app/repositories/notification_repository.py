from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from app.repositories.base import BaseRepository
from app.models.notification import Notification
from app.models.userNotification import UserNotification


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: Session):
        super().__init__(Notification, db)
    
    def create_notification(
        self, 
        title: str,
        content: str,
        type: str = "system",
        sender_id: Optional[str] = None,
        order_id: Optional[str] = None,
        is_global: bool = False,
        created_by: Optional[str] = None
    ) -> Notification:
        """Tạo notification mới"""
        notification = Notification(
            title=title,
            content=content,
            type=type,
            sender_id=sender_id,
            order_id=order_id,
            is_global=is_global
        )
        self.db.add(notification)
        self.db.flush()
        
        if created_by:
            notification.created_by = created_by
        
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def create_user_notification(
        self, 
        user_id: str, 
        notification_id: str
    ) -> UserNotification:
        """Tạo liên kết notification với user"""
        user_notification = UserNotification(
            user_id=user_id,
            notification_id=notification_id,
            is_read=False
        )
        self.db.add(user_notification)
        self.db.commit()
        self.db.refresh(user_notification)
        return user_notification
    
    def get_user_notifications(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False
    ) -> Tuple[List[UserNotification], int]:
        """Lấy danh sách notifications của user với phân trang"""
        query = self.db.query(UserNotification).filter(
            UserNotification.user_id == user_id,
            UserNotification.deleted_at.is_(None)
        )
        
        if unread_only:
            query = query.filter(UserNotification.is_read == False)
        
        total = query.count()
        
        items = query.order_by(
            desc(UserNotification.created_at)
        ).offset(skip).limit(limit).all()
        
        return items, total
    
    def get_unread_count(self, user_id: str) -> int:
        """Đếm số notification chưa đọc của user"""
        return self.db.query(UserNotification).filter(
            UserNotification.user_id == user_id,
            UserNotification.is_read == False,
            UserNotification.deleted_at.is_(None)
        ).count()
    
    def mark_as_read(self, notification_id: str, user_id: str) -> Optional[UserNotification]:
        """Đánh dấu notification đã đọc - tìm theo user_notification.id hoặc notification_id"""
        from sqlalchemy import or_
        
        user_notification = self.db.query(UserNotification).filter(
            or_(
                UserNotification.id == notification_id,
                UserNotification.notification_id == notification_id
            ),
            UserNotification.user_id == user_id,
            UserNotification.deleted_at.is_(None)
        ).first()
        
        if user_notification:
            user_notification.is_read = True
            user_notification.read_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user_notification)
        
        return user_notification
    
    def mark_all_as_read(self, user_id: str) -> int:
        """Đánh dấu tất cả notifications của user đã đọc"""
        count = self.db.query(UserNotification).filter(
            UserNotification.user_id == user_id,
            UserNotification.is_read == False,
            UserNotification.deleted_at.is_(None)
        ).update({
            UserNotification.is_read: True,
            UserNotification.read_at: datetime.utcnow()
        })
        self.db.commit()
        return count
    
    def get_user_notification_by_id(
        self, 
        notification_id: str, 
        user_id: str
    ) -> Optional[UserNotification]:
        """Lấy user notification theo ID hoặc notification_id"""
        from sqlalchemy import or_
        
        return self.db.query(UserNotification).filter(
            or_(
                UserNotification.id == notification_id,
                UserNotification.notification_id == notification_id
            ),
            UserNotification.user_id == user_id,
            UserNotification.deleted_at.is_(None)
        ).first()

