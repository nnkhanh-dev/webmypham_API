from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import AuditMixin


class UserNotification(AuditMixin, Base):
    __tablename__ = "user_notifications"
    user_id = Column(String(36), ForeignKey("users.id"))
    notification_id = Column(String(36), ForeignKey("notifications.id"))
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    notification = relationship("Notification", back_populates="user_notifications")

