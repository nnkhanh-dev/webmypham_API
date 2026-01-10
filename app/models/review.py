from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import AuditMixin


class Review(AuditMixin, Base):
    __tablename__ = "reviews"
    product_id = Column(String(36), ForeignKey("products.id"))
    user_id = Column(String(36), ForeignKey("users.id"))
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=True)  # Liên kết với đơn hàng
    rating = Column(Integer)
    comment = Column(String(255))
    medias = relationship("ReviewMedia", back_populates="review")
    order = relationship("Order")  # Relationship với Order
    user = relationship("User")  # Relationship với User

