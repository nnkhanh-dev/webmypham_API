from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mixins import AuditMixin


class Payment(AuditMixin, Base):
    __tablename__ = "payments"
    order_id = Column(String(36), ForeignKey("orders.id"))
    method = Column(String(50))  # COD, SEPAY
    status = Column(String(50))  # pending, success, failed
    transaction_id = Column(String(100), nullable=True)  # Mã giao dịch từ SePay
    amount = Column(Float, nullable=True)  # Số tiền thanh toán
    
    order = relationship("Order", back_populates="payment")