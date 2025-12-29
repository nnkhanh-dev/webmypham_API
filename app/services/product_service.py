from sqlalchemy.orm import Session
from app.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def get_detail(self, id: str):
        return self.repo.get_detail(id)

    def get_best_selling(self, limit=10):
        return self.repo.get_best_selling(limit)

    def get_most_favorite(self, limit=10):
        return self.repo.get_most_favorite(limit)