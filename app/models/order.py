from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import AuditMixin


class Order(AuditMixin, Base):
    __tablename__ = "orders"
    user_id = Column(String(36), ForeignKey("users.id"))
    address_id = Column(String(36), ForeignKey("addresses.id"), nullable=True)
    voucher_id = Column(String(36), ForeignKey("vouchers.id"), nullable=True)
    status = Column(String(50))  # pending, paid, processing, shipping, delivered, cancelled
    payment_method = Column(String(50))  # COD, SEPAY
    total_amount = Column(Float)  # Tổng tiền trước giảm giá
    discount_amount = Column(Float)  # Số tiền giảm
    final_amount = Column(Float)  # Số tiền cuối cùng
    note = Column(String(500), nullable=True)
    
    # Relationships
    details = relationship("OrderDetail", back_populates="order")
    payment = relationship("Payment", uselist=False, back_populates="order")
    address = relationship("Address")
    voucher = relationship("Voucher")
    user = relationship("User")