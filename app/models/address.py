from sqlalchemy import String, Boolean, ForeignKey, Column
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import AuditMixin

class Address(AuditMixin, Base):
    __tablename__ = "addresses"
    full_name = Column(String(100))
    phone_number = Column(String(20))
    province = Column(String(100))
    district = Column(String(100))
    ward = Column(String(100))
    detail = Column(String(255))
    is_default = Column(Boolean, default = False)
    user_id = Column(String(36), ForeignKey("users.id"))
    user = relationship("User", back_populates="addresses", foreign_keys=[user_id])
