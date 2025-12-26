from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.orm import relationship
from app.db.database import Base

# ensure junction table class is defined before relationships are configured
import app.models.userRole  # noqa: F401

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    created_by = Column(Integer, nullable=True, index=True)
    updated_by = Column(Integer, nullable=True, index=True)
    deleted_by = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP"))
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # relationship to users via user_roles junction table
    users = relationship("User", secondary="user_roles", back_populates="roles")
