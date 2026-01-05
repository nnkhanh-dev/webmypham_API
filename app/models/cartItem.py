from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import AuditMixin


class CartItem(AuditMixin, Base):
    __tablename__ = "cart_items"
    cart_id = Column(String(36), ForeignKey("carts.id"))
    product_type_id = Column(String(36), ForeignKey("product_types.id"))
    quantity = Column(Integer)
    cart = relationship("Cart", back_populates="items")
    product_type = relationship("ProductType")  # Thêm relationship để load thông tin sản phẩm

