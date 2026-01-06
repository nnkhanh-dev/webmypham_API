from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.product import Product
from app.models.productType import ProductType  
from app.models.review import Review
from app.models.wishlist import Wishlist
from app.models.order import Order
from app.models.orderDetail import OrderDetail
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repository cho Product với các method truy vấn sản phẩm"""

    def __init__(self, db: Session):
        super().__init__(Product, db)

    def get_detail(self, product_id: str) -> Optional[Product]:
        """Lấy chi tiết sản phẩm theo ID"""
        return self.db.query(Product).filter(
            Product.id == product_id,
            Product.deleted_at.is_(None),
            Product.is_active == True
        ).first()

    def get_by_brand(self, brand_id: str, limit: int = 20, skip: int = 0) -> List[Product]:
        """Lấy danh sách sản phẩm theo brand"""
        return self.db.query(Product).filter(
            Product.brand_id == brand_id,
            Product.deleted_at.is_(None),
            Product.is_active == True
        ).offset(skip).limit(limit).all()

    def get_by_category(self, category_id: str, limit: int = 20, skip: int = 0) -> List[Product]:
        """Lấy danh sách sản phẩm theo category"""
        return self.db.query(Product).filter(
            Product.category_id == category_id,
            Product.deleted_at.is_(None),
            Product.is_active == True
        ).offset(skip).limit(limit).all()

    def get_best_selling(self, limit: int = 10) -> List[Tuple[Product, int]]:
        """Lấy top sản phẩm bán chạy nhất (tính từ order_details với đơn hoàn thành)"""
        # Subquery: tính tổng số lượng bán của mỗi product_type
        sold_subquery = self.db.query(
            OrderDetail.product_type_id,
            func.sum(OrderDetail.number).label('quantity_sold')
        ).join(
            Order, Order.id == OrderDetail.order_id
        ).filter(
            Order.status.in_(['completed', 'delivered', 'COMPLETED', 'DELIVERED']),  # Chỉ tính đơn hoàn thành
            Order.deleted_at.is_(None),
            OrderDetail.deleted_at.is_(None)
        ).group_by(OrderDetail.product_type_id).subquery()

        # Query chính: join product với subquery
        return self.db.query(
            Product,
            func.coalesce(func.sum(sold_subquery.c.quantity_sold), 0).label('total_sold')
        ).join(
            ProductType, Product.id == ProductType.product_id
        ).outerjoin(
            sold_subquery, ProductType.id == sold_subquery.c.product_type_id
        ).filter(
            Product.deleted_at.is_(None),
            Product.is_active == True
        ).group_by(Product.id).order_by(
            desc('total_sold')
        ).limit(limit).all()

    def get_most_favorite(self, limit: int = 10) -> List[Tuple[Product, int]]:
        """Lấy top sản phẩm được yêu thích nhất (dựa vào số lượng trong wishlist)"""
        return self.db.query(Product, func.count(Wishlist.id).label('favorite_count')).join(
            Wishlist, Product.id == Wishlist.product_id
        ).filter(
            Product.deleted_at.is_(None),
            Product.is_active == True
        ).group_by(Product.id).order_by(
            desc('favorite_count')
        ).limit(limit).all()

    def get_top_rated(self, limit: int = 10) -> List[Tuple[Product, float, int]]:
        """Lấy top sản phẩm rating cao nhất (dựa vào trung bình rating từ reviews)"""
        return self.db.query(
            Product,
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('review_count')
        ).join(
            Review, Product.id == Review.product_id
        ).filter(
            Product.deleted_at.is_(None),
            Product.is_active == True,
            Review.deleted_at.is_(None)
        ).group_by(Product.id).having(
            func.count(Review.id) >= 1  # Chỉ lấy sản phẩm có ít nhất 1 review
        ).order_by(
            desc('avg_rating'),
            desc('review_count')
        ).limit(limit).all()

    def get_new_arrivals(self, limit: int = 10) -> List[Product]:
        """Lấy sản phẩm mới nhất"""
        return self.db.query(Product).filter(
            Product.deleted_at.is_(None),
            Product.is_active == True
        ).order_by(
            desc(Product.created_at)
        ).limit(limit).all()