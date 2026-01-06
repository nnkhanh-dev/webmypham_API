from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, or_
from app.models.product import Product
from app.models.productType import ProductType  
from app.models.review import Review
from app.models.wishlist import Wishlist
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repository cho Product với các method truy vấn sản phẩm"""

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
        """Lấy top sản phẩm bán chạy nhất (dựa vào số lượng đã bán của product_types)"""
        return self.db.query(Product, func.sum(ProductType.sold).label('total_sold')).join(
            ProductType, Product.id == ProductType.product_id
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