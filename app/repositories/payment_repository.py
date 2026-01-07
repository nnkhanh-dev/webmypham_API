from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.payment import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: Session):
        super().__init__(Payment, db)

    def get_by_order_id(self, order_id: str) -> Optional[Payment]:
        """Lấy payment theo order_id (bất kỳ status nào)"""
        return self.db.query(Payment)\
            .filter(Payment.order_id == order_id)\
            .order_by(Payment.created_at.desc())\
            .first()

    def get_active_by_order_id(self, order_id: str) -> Optional[Payment]:
        """Lấy payment active (pending/cod_pending/success) của order"""
        return self.db.query(Payment)\
            .filter(
                Payment.order_id == order_id,
                Payment.status.in_(["pending", "cod_pending", "success"])
            )\
            .order_by(Payment.created_at.desc())\
            .first()

    def get_pending_by_order_id(self, order_id: str) -> Optional[Payment]:
        """Lấy payment đang pending (pending/cod_pending) của order"""
        return self.db.query(Payment)\
            .filter(
                Payment.order_id == order_id,
                Payment.status.in_(["pending", "cod_pending"])
            ).first()

    def update_status(self, payment_id: str, status: str, transaction_id: Optional[str] = None) -> bool:
        """Cập nhật trạng thái payment"""
        payment = self.get(payment_id)
        if not payment:
            return False
        payment.status = status
        if transaction_id:
            payment.transaction_id = transaction_id
        self.db.commit()
        return True

    def update_status_by_order(self, order_id: str, old_status: str, new_status: str) -> bool:
        """Cập nhật status của payment theo order_id"""
        payment = self.db.query(Payment).filter(
            Payment.order_id == order_id,
            Payment.status == old_status
        ).first()
        if not payment:
            return False
        payment.status = new_status
        self.db.commit()
        return True

    def create_payment(self, payment_data: dict) -> Payment:
        """Tạo payment mới"""
        payment = Payment(**payment_data)
        self.db.add(payment)
        self.db.flush()
        return payment
