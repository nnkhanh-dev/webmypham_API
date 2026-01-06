from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from app.repositories.product_repository import ProductRepository
from app.schemas.request.product import ProductCreateRequest, ProductUpdateRequest
# from sqlalchemy.orm import Session
# from app.repositories.product_repository import ProductRepository

# class ProductService:
#     def __init__(self, db: Session):
#         self.repo = ProductRepository(db)

#     def get_detail(self, id: str):
#         return self.repo.get_detail(id)

    def get_all(self, skip: int = 0, limit: int = 20):
        """Lấy danh sách tất cả sản phẩm với phân trang"""
        return self.repo.get_all(skip=skip, limit=limit)

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
    ) -> Tuple[List, int]:
        """Tìm kiếm và lọc sản phẩm"""
        return self.repo.search_with_filters(
            keyword=keyword,
            brand_id=brand_id,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )

    def create(self, data: ProductCreateRequest, created_by: Optional[str] = None):
        """Tạo sản phẩm mới"""
        product_data = data.model_dump(exclude={"product_types"})
        product = self.repo.create(product_data, created_by=created_by)
        return product

    def update(self, id: str, data: ProductUpdateRequest, updated_by: Optional[str] = None):
        """Cập nhật sản phẩm"""
        update_data = data.model_dump(exclude_unset=True, exclude={"product_types"})
        return self.repo.update(id, update_data, updated_by=updated_by)

    def delete(self, id: str, deleted_by: Optional[str] = None) -> bool:
        """Soft delete sản phẩm"""
        return self.repo.delete(id, deleted_by=deleted_by)

    def get_best_selling(self, limit=10):
        return self.repo.get_best_selling(limit)
#     def get_best_selling(self, limit=10):
#         return self.repo.get_best_selling(limit)

#     def get_most_favorite(self, limit=10):
#         return self.repo.get_most_favorite(limit)

#     def get_by_brand(self, brand_id: str, limit=20, skip=0):
#         return self.repo.get_by_brand(brand_id, limit, skip)

#     def get_by_category(self, category_id: str, limit=20, skip=0):
#         return self.repo.get_by_category(category_id, limit, skip)