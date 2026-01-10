from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import AuditMixin


class Wishlist(AuditMixin, Base):
    __tablename__ = "wishlists"
    __table_args__ = (
        UniqueConstraint('user_id', 'deleted_at', name='uq_user_wishlist'),
        Index('ix_wishlists_user_id', 'user_id'),
        Index('ix_wishlists_deleted_at', 'deleted_at'),
    )
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    items = relationship("WishlistItem", back_populates="wishlist", cascade="all, delete-orphan")

