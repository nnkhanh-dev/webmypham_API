from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: str) -> Optional[Category]:
    repo = CategoryRepository(db)
    return repo.get(category_id)


def get_categories(db: Session, skip: int = 0, limit: int = 100, q: Optional[str] = None, sort_by: str = "id", sort_dir: str = "desc") -> Tuple[List[Category], int]:
    repo = CategoryRepository(db)
    return repo.search(skip=skip, limit=limit, q=q, sort_by=sort_by, sort_dir=sort_dir)


def create_category(db: Session, category_in: CategoryCreate, created_by: Optional[str] = None) -> Category:
    repo = CategoryRepository(db)
    return repo.create(category_in.dict(), created_by=created_by)


def update_category(db: Session, category_id: str, category_in: CategoryUpdate, updated_by: Optional[str] = None) -> Optional[Category]:
    repo = CategoryRepository(db)
    data = category_in.dict(exclude_unset=True)
    return repo.update(category_id, data, updated_by=updated_by)


def delete_category(db: Session, category_id: str, deleted_by: Optional[str] = None) -> bool:
    repo = CategoryRepository(db)
    return repo.delete(category_id, deleted_by=deleted_by)


def get_category_children(db: Session, category_id: str) -> List[Category]:
    repo = CategoryRepository(db)
    return repo.list_children(category_id)
