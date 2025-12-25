from sqlalchemy import Column, Integer, String, Float, DateTime, text
from app.db.database import Base

class Voucher(Base):
    __tablename__ = "vouchers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    discount = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    created_by = Column(Integer, nullable=True, index=True)
    updated_by = Column(Integer, nullable=True, index=True)
    deleted_by = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP"))
    deleted_at = Column(DateTime(timezone=True), nullable=True)

