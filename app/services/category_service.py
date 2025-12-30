from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.request.category import CategoryCreate, CategoryUpdate
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
    # normalize empty parent_id to None (client may send empty string)
    parent_id = data.get("parent_id")
    if parent_id == "" or parent_id is None:
        data["parent_id"] = None
    else:
        # verify parent exists
        parent = repo.get(parent_id)
        if not parent:
            raise ValueError("Danh mục cha không tồn tại.")
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


def get_category_tree(db: Session, max_depth: int = 3) -> List[dict]:
    """Return list of categories (top-level) each containing nested `children` up to `max_depth` levels.

    The returned structure is a list of dicts suitable for Pydantic parsing by `CategoryResponse`.
    """
    repo = CategoryRepository(db)

    def to_dict(cat):
        return {
            "id": cat.id,
            "name": cat.name,
            "slug": getattr(cat, "slug", None),
            "image_path": getattr(cat, "image_path", None),
            "description": getattr(cat, "description", None),
            "parent_id": getattr(cat, "parent_id", None),
            "created_by": getattr(cat, "created_by", None),
            "updated_by": getattr(cat, "updated_by", None),
            "deleted_by": getattr(cat, "deleted_by", None),
            "created_at": getattr(cat, "created_at", None),
            "updated_at": getattr(cat, "updated_at", None),
            "deleted_at": getattr(cat, "deleted_at", None),
            "children": None,
        }

    def build(node, depth):
        if depth >= max_depth:
            return node
        children = repo.list_children(node["id"])
        if not children:
            node["children"] = []
            return node
        node["children"] = [build(to_dict(c), depth + 1) for c in children]
        return node

    # top-level categories (parent_id is None)
    tops = db.query(Category).filter(Category.parent_id.is_(None), Category.deleted_at.is_(None)).all()
    tree = [build(to_dict(c), 1) for c in tops]
    return tree


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
