from sqlalchemy import String, ForeignKey, Column, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import AuditMixin

class Message(AuditMixin, Base):
    __tablename__ = "messages"
    conversation_id = Column(String(36), ForeignKey("conversations.id"))
    sender_id = Column(String(36), ForeignKey("users.id"))
    message = Column(Text)
    is_read = Column(Boolean, default=False)

    conversation = relationship("Conversation", back_populates="messages")


