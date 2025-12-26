from sqlalchemy import Column, Integer, DateTime, text, ForeignKey
from app.db.database import Base

class UserRole(Base):
    __tablename__ = "user_roles"

    # composite primary key (user_id, role_id)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)

    created_by = Column(Integer, nullable=True, index=True)
    updated_by = Column(Integer, nullable=True, index=True)
    deleted_by = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP"))
    deleted_at = Column(DateTime(timezone=True), nullable=True)

