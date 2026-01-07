from sqlalchemy import String, Column, ForeignKey, Float, Integer, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import AuditMixin


class ProductType(AuditMixin, Base):
    __tablename__ = "product_types"
    product_id = Column(String(36), ForeignKey("products.id"))
    type_value_id = Column(String(36), ForeignKey("type_values.id"))
    image_path = Column(String(255))
    price = Column(Float)
    status = Column(String(50))
    quantity = Column(Integer)
    stock = Column(Integer)
    discount_price = Column(Float)
    volume = Column(String(50))
    ingredients = Column(Text)
    usage = Column(String(255))
    skin_type = Column(String(100))
    origin = Column(String(100))
    product = relationship("Product", back_populates="product_types")
    type_value = relationship("TypeValue")  # Thêm relationship để load tên biến thể (màu sắc, dung tích...)
