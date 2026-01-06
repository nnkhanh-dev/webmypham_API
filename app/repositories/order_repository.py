from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from app.models.order import Order
from app.models.orderDetail import OrderDetail
from app.repositories.base import BaseRepository
from sqlalchemy.orm import joinedload


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session):
        super().__init__(Order, db)

    def get_by_user(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Order]:
        """Lấy danh sách đơn hàng của user"""
        return self.db.query(Order)\
            .filter(Order.user_id == user_id, Order.deleted_at.is_(None))\
            .order_by(Order.created_at.desc())\
            .offset(skip).limit(limit).all()

    def get_detail(self, order_id: str) -> Optional[Order]:
        """Lấy chi tiết đơn hàng với order details"""
        return self.db.query(Order)\
            .options(joinedload(Order.details))\
            .filter(Order.id == order_id, Order.deleted_at.is_(None))\
            .first()

    def get_by_id_and_user(self, order_id: str, user_id: str) -> Optional[Order]:
        """Lấy đơn hàng theo ID và user_id"""
        return self.db.query(Order)\
            .options(joinedload(Order.details))\
            .filter(
                Order.id == order_id,
                Order.user_id == user_id,
                Order.deleted_at.is_(None)
            ).first()

    def get_pending_sepay_expired(self, timeout_minutes: int = 15) -> List[Order]:
        """Lấy các đơn SEPAY pending đã quá thời gian thanh toán"""
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        return self.db.query(Order)\
            .options(joinedload(Order.details))\
            .filter(
                Order.status == "pending",
                Order.payment_method == "SEPAY",
                Order.created_at < cutoff_time,
                Order.deleted_at.is_(None)
            ).all()

    def update_status(self, order_id: str, status: str) -> bool:
        """Cập nhật trạng thái đơn hàng"""
        order = self.get(order_id)
        if not order:
            return False
        order.status = status
        self.db.commit()
        return True

    def create_order(self, order_data: dict, order_details: List[dict]) -> Order:
        """Tạo đơn hàng mới với order details"""
        order = Order(**order_data)
        self.db.add(order)
        self.db.flush()
        
        for detail_data in order_details:
            detail = OrderDetail(**detail_data, order_id=order.id)
            self.db.add(detail)
        
        return order