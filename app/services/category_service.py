from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate
from slugify import slugify


def get_category(db: Session, category_id: str) -> Optional[Category]:
    repo = CategoryRepository(db)
    return repo.get(category_id)


def get_categories(db: Session, skip: int = 0, limit: int = 100, q: Optional[str] = None, sort_by: str = "id", sort_dir: str = "desc") -> Tuple[List[Category], int]:
    repo = CategoryRepository(db)
    return repo.search(skip=skip, limit=limit, q=q, sort_by=sort_by, sort_dir=sort_dir)


def create_category(db: Session, category_in: CategoryCreate, created_by: Optional[str] = None) -> Category:
    repo = CategoryRepository(db)
    data = category_in.dict()
    # generate slug from name
    name = data.get("name", "")
    slug_base = _slugify(name)
    slug = _make_unique_slug(db, Category, slug_base)
    data["slug"] = slug
    return repo.create(data, created_by=created_by)


def update_category(db: Session, category_id: str, category_in: CategoryUpdate, updated_by: Optional[str] = None) -> Optional[Category]:
    repo = CategoryRepository(db)
    data = category_in.dict(exclude_unset=True)
    # if name updated and slug not explicitly provided, regenerate slug
    if "name" in data and "slug" not in data:
        slug_base = _slugify(data.get("name"))
        data["slug"] = _make_unique_slug(db, Category, slug_base, exclude_id=category_id)
    return repo.update(category_id, data, updated_by=updated_by)


def delete_category(db: Session, category_id: str, deleted_by: Optional[str] = None) -> bool:
    repo = CategoryRepository(db)
    return repo.delete(category_id, deleted_by=deleted_by)


def get_category_children(db: Session, category_id: str) -> List[Category]:
    repo = CategoryRepository(db)
    return repo.list_children(category_id)


def _slugify(value: str) -> str:
    return slugify(value or "", lowercase=True) or "n-a"


def _make_unique_slug(db: Session, model, base: str, exclude_id: Optional[str] = None) -> str:
    exists = db.query(model).filter(model.slug == base)
    if exclude_id:
        exists = exists.filter(model.id != exclude_id)
    if exists.first():
        like_pattern = f"{base}-%"
        rows = db.query(model.slug).filter(model.slug.ilike(like_pattern)).all()
        suffixes = [int(r[0].rsplit("-", 1)[1]) for r in rows if r[0].rsplit("-", 1)[-1].isdigit()]
        next_suffix = (max(suffixes) + 1) if suffixes else 2
        return f"{base}-{next_suffix}"
    return base
