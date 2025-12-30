from sqlalchemy import String, Column
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import AuditMixin

class Brand(AuditMixin, Base):
    __tablename__ = "brands"
    name = Column(String(100))
    slug = Column(String(100), unique=True, index=True)
    image_path = Column(String(255))
    description = Column(String(255))
    products = relationship("Product", back_populates="brand")

