# from sqlalchemy.orm import Session
# from app.repositories.product_repository import ProductRepository

# class ProductService:
#     def __init__(self, db: Session):
#         self.repo = ProductRepository(db)

#     def get_detail(self, id: str):
#         return self.repo.get_detail(id)

#     def get_best_selling(self, limit=10):
#         return self.repo.get_best_selling(limit)

#     def get_most_favorite(self, limit=10):
#         return self.repo.get_most_favorite(limit)

#     def get_by_brand(self, brand_id: str, limit=20, skip=0):
#         return self.repo.get_by_brand(brand_id, limit, skip)

#     def get_by_category(self, category_id: str, limit=20, skip=0):
#         return self.repo.get_by_category(category_id, limit, skip)