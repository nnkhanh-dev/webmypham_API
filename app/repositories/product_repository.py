from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, or_, exists
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from app.models.product import Product
from app.models.productType import ProductType
from app.models.typeValue import TypeValue
from app.models.orderDetail import OrderDetail
from app.models.review import Review
from app.models.wishlist import Wishlist
from app.repositories.base import BaseRepository
from app.schemas.response.product import ProductDetailResponse

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
        
        # Base query with relationships
        query = self.db.query(Product).filter(Product.deleted_at.is_(None)).options(
            joinedload(Product.brand),
            joinedload(Product.category),
            joinedload(Product.product_types)
        )
        
        # Chỉ lấy sản phẩm có ít nhất 1 product type
        from sqlalchemy import select, and_
        has_product_type = select(ProductType.id).where(
            and_(
                ProductType.product_id == Product.id,
                ProductType.deleted_at.is_(None)
            )
        ).correlate(Product).exists()
        query = query.filter(has_product_type)
        
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

    def get_detail(self, product_id: str):
        product = self.db.query(Product)\
            .options(
                joinedload(Product.brand),
                joinedload(Product.category),
                joinedload(Product.product_types)
                    .joinedload(ProductType.type_value)
                    .joinedload(TypeValue.type)
            )\
            .filter(
                Product.id == product_id,
                Product.deleted_at.is_(None),
                Product.is_active == True
            ).first()
        if not product:
            return None
        return ProductDetailResponse.model_validate(product)

    def get_by_brand(self, brand_id: str, limit: int = 20, skip: int = 0):
        """Lấy danh sách sản phẩm theo brand"""
        return self.db.query(Product).filter(
            Product.brand_id == brand_id,
            Product.deleted_at.is_(None),
            Product.is_active == True,
        ).options(joinedload(Product.product_types)).offset(skip).limit(limit).all()

    def get_by_category(self, category_id: str, limit: int = 20, skip: int = 0):
        """Lấy danh sách sản phẩm theo category"""
        return self.db.query(Product).filter(
            Product.category_id == category_id,
            Product.deleted_at.is_(None),
            Product.is_active == True,
        ).options(joinedload(Product.product_types)).offset(skip).limit(limit).all()

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
