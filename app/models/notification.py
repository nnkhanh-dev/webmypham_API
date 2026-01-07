from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import AuditMixin


class Notification(AuditMixin, Base):
    __tablename__ = "notifications"
    title = Column(String(200))
    content = Column(Text)  # Fixed: was Boolean, now Text
    type = Column(String(50))  # order, system, promotion, etc.
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=True)  # Link to order if type='order'
    is_global = Column(Boolean, default=False)  # If true, send to all users
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    order = relationship("Order", foreign_keys=[order_id])
    user_notifications = relationship("UserNotification", back_populates="notification")

