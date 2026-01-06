from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from app.models.product import Product
from app.models.orderDetail import OrderDetail
from app.models.review import Review
from app.models.wishlist import Wishlist
from app.models.order import Order
from app.models.orderDetail import OrderDetail

from app.repositories.base import BaseRepository

class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(Product, db)

    def search_with_filters(
        self,
        keyword: Optional[str] = None,
        brand_id: Optional[str] = None,
        category_id: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        is_active: Optional[bool] = True,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Product], int]:
        """
        Tìm kiếm và lọc sản phẩm với nhiều điều kiện
        Returns: (list of products, total count)
        """
        # Base query
        query = self.db.query(Product).filter(Product.deleted_at.is_(None))
        
        # Filter by is_active
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        
        # Search by keyword (name or description)
        if keyword:
            search_term = f"%{keyword}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        
        # Filter by brand
        if brand_id:
            query = query.filter(Product.brand_id == brand_id)
        
        # Filter by category
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        # Filter by price range (using ProductType's price)
        if min_price is not None or max_price is not None:
            query = query.join(ProductType, Product.id == ProductType.product_id)
            if min_price is not None:
                query = query.filter(ProductType.price >= min_price)
            if max_price is not None:
                query = query.filter(ProductType.price <= max_price)
            query = query.distinct()
        
        # Get total count before pagination
        total_count = query.count()
        
        # Sorting
        sort_column = getattr(Product, sort_by, Product.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        
        # Pagination
        products = query.offset(skip).limit(limit).all()
        
        return products, total_count

    def get_detail(self, product_id: str) -> Optional[Product]:
        """Lấy chi tiết sản phẩm theo ID"""
        return self.db.query(Product).filter(
            Product.id == product_id,
            Product.deleted_at.is_(None),
            Product.is_active == True
        ).first()

    def get_by_brand(self, brand_id: str, limit: int = 20, skip: int = 0) -> List[Product]:
        """Lấy danh sách sản phẩm theo brand"""
    def get_detail(self, id: str):
        return self.db.query(Product)\
            .options(
                joinedload(Product.brand),
                joinedload(Product.category),
                joinedload(Product.product_types)
            )\
            .filter(Product.id == id, Product.deleted_at.is_(None))\
            .first()

    def get_by_brand(self, brand_id: str, limit: int = 20, skip: int = 0):
        return self.db.query(Product).filter(
            Product.brand_id == brand_id,
            Product.deleted_at.is_(None),
            Product.is_active == True,
        ).options(joinedload(Product.product_types)).offset(skip).limit(limit).all()

    def get_by_category(self, category_id: str, limit: int = 20, skip: int = 0):
        return self.db.query(Product).filter(
            Product.category_id == category_id,
            Product.deleted_at.is_(None),
            Product.is_active == True,
        ).options(joinedload(Product.product_types)).offset(skip).limit(limit).all()

    # def get_best_selling(self, limit: int = 10) -> List[Tuple[Product, int]]:
    #     """Lấy top sản phẩm bán chạy nhất (tính từ order_details với đơn hoàn thành)"""
    #     # Subquery: tính tổng số lượng bán của mỗi product_type
    #     sold_subquery = self.db.query(
    #         OrderDetail.product_type_id,
    #         func.sum(OrderDetail.number).label('quantity_sold')
    #     ).join(
    #         Order, Order.id == OrderDetail.order_id
    #     ).filter(
    #         Order.status.in_(['completed', 'delivered', 'COMPLETED', 'DELIVERED']),  # Chỉ tính đơn hoàn thành
    #         Order.deleted_at.is_(None),
    #         OrderDetail.deleted_at.is_(None)
    #     ).group_by(OrderDetail.product_type_id).subquery()

    #     # Query chính: join product với subquery
    #     return self.db.query(
    #         Product,
    #         func.coalesce(func.sum(sold_subquery.c.quantity_sold), 0).label('total_sold')
    #     ).join(
    #         ProductType, Product.id == ProductType.product_id
    #     ).outerjoin(
    #         sold_subquery, ProductType.id == sold_subquery.c.product_type_id
    #     ).filter(
    #         Product.deleted_at.is_(None),
    #         Product.is_active == True
    #     ).group_by(Product.id).order_by(
    #         desc('total_sold')
    #     ).limit(limit).all()

    # def get_most_favorite(self, limit: int = 10) -> List[Tuple[Product, int]]:
    #     """Lấy top sản phẩm được yêu thích nhất (dựa vào số lượng trong wishlist)"""
    #     return self.db.query(Product, func.count(Wishlist.id).label('favorite_count')).join(
    #         Wishlist, Product.id == Wishlist.product_id
    #     ).filter(
    #         Product.deleted_at.is_(None),
    #         Product.is_active == True
    #     ).group_by(Product.id).order_by(
    #         desc('favorite_count')
    #     ).limit(limit).all()

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

    def get_best_selling(self, limit: int = 10):
        return self.db.query(
                Product,
                func.sum(OrderDetail.quantity).label("total_sold")
            )\
            .join(OrderDetail, OrderDetail.product_id == Product.id)\
            .filter(Product.deleted_at.is_(None), Product.is_active == True)\
            .group_by(Product.id)\
            .order_by(desc("total_sold"))\
            .limit(limit)\
            .all()

    def get_most_favorite(self, limit: int = 10):
        return self.db.query(
                Product,
                func.avg(Review.rating).label("avg_rating")
            )\
            .join(Review, Review.product_id == Product.id)\
            .filter(Product.deleted_at.is_(None), Product.is_active == True)\
            .group_by(Product.id)\
            .order_by(desc("avg_rating"))\
            .limit(limit)\
            .all()
