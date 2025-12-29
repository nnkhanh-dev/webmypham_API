from sqlalchemy.orm import Session, joinedload
from app.models.product import Product
from app.repositories.base import BaseRepository
from sqlalchemy import func, desc

class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(Product, db)

    def get_detail(self, id: str):
        return self.db.query(Product)\
            .options(
                joinedload(Product.brand),
                joinedload(Product.category),
                joinedload(Product.product_types)
            )\
            .filter(Product.id == id, Product.deleted_at.is_(None))\
            .first()

    def get_best_selling(self, limit: int = 10):
        from app.models.orderDetail import OrderDetail
        # Đếm tổng quantity đã bán group by product
        return self.db.query(
                Product,
                func.sum(OrderDetail.quantity).label("total_sold")
            )\
            .join(OrderDetail, OrderDetail.product_id == Product.id)\
            .group_by(Product.id)\
            .order_by(desc("total_sold"))\
            .limit(limit)\
            .all()

    def get_most_favorite(self, limit: int = 10):
        from app.models.review import Review
        # Lấy sản phẩm có rating trung bình cao nhất
        return self.db.query(
                Product,
                func.avg(Review.rating).label("avg_rating")
            )\
            .join(Review, Review.product_id == Product.id)\
            .group_by(Product.id)\
            .order_by(desc("avg_rating"))\
            .limit(limit)\
            .all()