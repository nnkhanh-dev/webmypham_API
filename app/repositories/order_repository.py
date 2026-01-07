from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc
from app.models.order import Order
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session):
        super().__init__(Order, db)

    def get_by_user(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 20,
        status: Optional[str] = None,
        sort_order: str = "desc"
    ) -> Tuple[List[Order], int]:
        """Lấy danh sách đơn hàng của user với phân trang và filter"""
        query = self.db.query(Order).filter(
            Order.user_id == user_id,
            Order.deleted_at.is_(None)
        )
        
        # Filter by status
        if status:
            query = query.filter(Order.status == status)
        
        # Get total count
        total = query.count()
        
        # Sorting
        if sort_order.lower() == "asc":
            query = query.order_by(asc(Order.created_at))
        else:
            query = query.order_by(desc(Order.created_at))
        
        # Pagination
        orders = query.offset(skip).limit(limit).all()
        
        return orders, total

    def get_detail(self, order_id: str) -> Optional[Order]:
        """Lấy chi tiết đơn hàng kèm items và payment"""
        return self.db.query(Order)\
            .options(
                joinedload(Order.details),
                joinedload(Order.payment)
            )\
            .filter(Order.id == order_id, Order.deleted_at.is_(None))\
            .first()

    def get_user_order_detail(self, order_id: str, user_id: str) -> Optional[Order]:
        """Lấy chi tiết đơn hàng của user cụ thể (bảo mật)"""
        return self.db.query(Order)\
            .options(
                joinedload(Order.details),
                joinedload(Order.payment)
            )\
            .filter(
                Order.id == order_id,
                Order.user_id == user_id,
                Order.deleted_at.is_(None)
            )\
            .first()