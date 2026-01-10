from sqlalchemy.orm import Session, joinedload
from app.models.review import Review
from app.repositories.base import BaseRepository

class ReviewRepository(BaseRepository[Review]):
    def __init__(self, db: Session):
        super().__init__(Review, db)

    def get_by_product(self, product_id: str):
        return self.db.query(Review).options(
            joinedload(Review.user)
        ).filter(
            Review.product_id == product_id,
            Review.deleted_at.is_(None)
        ).order_by(Review.created_at.desc()).all()