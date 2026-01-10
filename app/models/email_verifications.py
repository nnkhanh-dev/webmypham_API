from sqlalchemy import String, ForeignKey, Column, Integer, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import AuditMixin

class EmailVerification(AuditMixin, Base):
    __tablename__ = "email_verifications"
    user_id = Column(String(36), ForeignKey("users.id"))
    code_hash = Column(String(255), nullable=False)  # Hash của mã 6 số
    attempts = Column(Integer, default=0)  # Số lần nhập sai
    resend_count = Column(Integer, default=0)  # Số lần gửi lại
    last_sent_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)  # Thời gian hết hạn (VD: 10 phút)
    verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)  # Vô hiệu hóa code cũ khi resend
    
    # Relationship
    user = relationship("User", back_populates="email_verifications")