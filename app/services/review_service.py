from sqlalchemy.orm import Session
from app.repositories.review_repository import ReviewRepository
from app.schemas.request.review import ReviewCreate, ReviewUpdate

class ReviewService:
    def __init__(self, db: Session):
        self.repo = ReviewRepository(db)

    def create(self, review_in: ReviewCreate):
        return self.repo.create(review_in.dict())

    def get(self, review_id: str):
        return self.repo.get(review_id)

    def update(self, review_id: str, review_in: ReviewUpdate):
        return self.repo.update(review_id, review_in.dict(exclude_unset=True))

    def delete(self, review_id: str):
        return self.repo.delete(review_id)

    def get_by_product(self, product_id: str):
        return self.repo.get_by_product(product_id)