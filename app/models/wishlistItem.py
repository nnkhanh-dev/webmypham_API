from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import AuditMixin

class WishlistItem(AuditMixin, Base):
    __tablename__ = "wishlist_items"
    __table_args__ = (
        UniqueConstraint('wishlist_id', 'product_type_id', 'deleted_at', name='uq_wishlist_product'),
        Index('ix_wishlist_items_wishlist_id', 'wishlist_id'),
        Index('ix_wishlist_items_product_type_id', 'product_type_id'),
        Index('ix_wishlist_items_deleted_at', 'deleted_at'),
    )
    
    wishlist_id = Column(String(36), ForeignKey("wishlists.id"), nullable=False)
    product_type_id = Column(String(36), ForeignKey("product_types.id"), nullable=False)
    wishlist = relationship("Wishlist", back_populates="items")
    product_type = relationship("ProductType", foreign_keys=[product_type_id])

