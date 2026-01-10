from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from app.core.database import Base
from app.models.mixins import AuditMixin
from sqlalchemy.orm import relationship
# ensure junction table class is defined before relationships are configured

class User(AuditMixin, Base):
    __tablename__ = "users"
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    dob = Column(DateTime, nullable=True)
    gender = Column(Integer, nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    reset_password_token = Column(Text, nullable=True)
    version = Column(Integer, default=1)
    email_confirmed = Column(Boolean, nullable=False, default=False)

    # relationship to roles via user_roles junction table
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    addresses = relationship("Address", back_populates="user")
    email_verifications = relationship("EmailVerification", back_populates="user")
