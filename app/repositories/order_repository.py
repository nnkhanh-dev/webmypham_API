from sqlalchemy.orm import Session
from app.models.order import Order
from app.repositories.base import BaseRepository
from sqlalchemy.orm import joinedload

class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session):
        super().__init__(Order, db)

    # Thêm các method custom nếu cần, ví dụ lấy orders theo user, tra cứu lịch sử:

    def get_by_user(self, user_id: str, skip: int = 0, limit: int = 20):
        return self.db.query(Order)\
            .filter(Order.user_id == user_id, Order.deleted_at.is_(None))\
            .offset(skip).limit(limit).all()

    def get_detail(self, order_id: str):
        return self.db.query(Order)\
            .options(joinedload(Order.details))\
            .filter(Order.id == order_id, Order.deleted_at.is_(None))\
            .first()