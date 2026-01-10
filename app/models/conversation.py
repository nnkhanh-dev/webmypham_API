from sqlalchemy import String, ForeignKey, Column, Text, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import AuditMixin

class Conversation(AuditMixin, Base):
    __tablename__ = "conversations"

    customer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    admin_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    
    last_message = Column(Text)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Track whether admin has read this conversation
    is_read = Column(Boolean, default=False, nullable=False, index=True)

    customer = relationship("User", foreign_keys=[customer_id], backref="customer_conversations")
    admin = relationship("User", foreign_keys=[admin_id], backref="admin_conversations")
    
    # Một hội thoại có nhiều tin nhắn
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")