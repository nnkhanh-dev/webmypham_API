from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc
from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(Category, db)

    def get_by_name(self, name: str) -> Optional[Category]:
        return self.db.query(Category).filter(
            Category.name == name,
            Category.deleted_at.is_(None),
        ).first()

    def search(self, skip: int = 0, limit: int = 100, q: Optional[str] = None, sort_by: str = "id", sort_dir: str = "desc") -> Tuple[List[Category], int]:
        query = self.db.query(Category).filter(Category.deleted_at.is_(None))
        if q:
            like = f"%{q}%"
            query = query.filter(or_(Category.name.ilike(like), Category.description.ilike(like)))
        total = query.count()
        sort_col = getattr(Category, sort_by, None)
        if sort_col is None:
            sort_col = Category.id
        if sort_dir and sort_dir.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))
        items = query.offset(skip).limit(limit).all()
        return items, total

    def list_children(self, parent_id: str) -> List[Category]:
        return self.db.query(Category).filter(Category.parent_id == parent_id, Category.deleted_at.is_(None)).all()
