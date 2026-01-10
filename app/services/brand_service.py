from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.brand import Brand
from app.repositories.brand_repository import BrandRepository
from app.schemas.request.brand import BrandCreate, BrandUpdate
from app.services.upload_product_service import save_upload_file, get_upload_url
from slugify import slugify


def get_brand(db: Session, brand_id: str) -> Optional[Brand]:
    repo = BrandRepository(db)
    return repo.get(brand_id)


def get_brand_by_name(db: Session, name: str) -> Optional[Brand]:
    repo = BrandRepository(db)
    return repo.get_by_name(name)


def get_brands(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = None,
    sort_by: str = "id",
    sort_dir: str = "desc",
) -> Tuple[List[Brand], int]:
    repo = BrandRepository(db)
    return repo.search(
        skip=skip,
        limit=limit,
        q=q,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


def create_brand(db: Session, brand_in: BrandCreate, created_by: Optional[str] = None) -> Brand:
    repo = BrandRepository(db)
    data = brand_in.dict()
    # generate slug from name
    name = data.get("name", "")
    slug_base = _slugify(name)
    slug = _make_unique_slug(db, Brand, slug_base)
    data["slug"] = slug
    return repo.create(data, created_by=created_by)


async def create_brand_with_image(
    db: Session,
    name: str,
    description: Optional[str] = None,
    image_file: Optional[UploadFile] = None,
    created_by: Optional[str] = None
) -> Brand:
    """
    Tạo brand mới với upload ảnh trực tiếp
    """
    repo = BrandRepository(db)
    
    # Upload image if provided
    image_path = None
    if image_file and image_file.filename:
        filename = await save_upload_file(image_file, subfolder="brands")
        image_path = get_upload_url(filename)
    
    # Prepare brand data
    data = {
        "name": name,
        "description": description,
        "image_path": image_path
    }
    
    # Generate slug
    slug_base = _slugify(name)
    slug = _make_unique_slug(db, Brand, slug_base)
    data["slug"] = slug
    
    return repo.create(data, created_by=created_by)


def update_brand(db: Session, brand_id: str, brand_in: BrandUpdate, updated_by: Optional[str] = None) -> Optional[Brand]:
    repo = BrandRepository(db)
    update_data = brand_in.dict(exclude_unset=True)
    # if name updated and slug not explicitly provided, regenerate slug
    if "name" in update_data and "slug" not in update_data:
        slug_base = _slugify(update_data.get("name"))
        update_data["slug"] = _make_unique_slug(db, Brand, slug_base, exclude_id=brand_id)
    return repo.update(brand_id, update_data, updated_by=updated_by)


async def update_brand_with_image(
    db: Session,
    brand_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    image_file: Optional[UploadFile] = None,
    updated_by: Optional[str] = None
) -> Optional[Brand]:
    """
    Cập nhật brand với upload ảnh trực tiếp
    """
    repo = BrandRepository(db)
    
    # Prepare update data
    update_data = {}
    
    if name is not None:
        update_data["name"] = name
        # Regenerate slug if name changed
        slug_base = _slugify(name)
        update_data["slug"] = _make_unique_slug(db, Brand, slug_base, exclude_id=brand_id)
    
    if description is not None:
        update_data["description"] = description
    
    # Upload new image if provided
    if image_file and image_file.filename:
        filename = await save_upload_file(image_file, subfolder="brands")
        image_path = get_upload_url(filename)
        update_data["image_path"] = image_path
    
    if not update_data:
        # No changes, return existing brand
        return repo.get(brand_id)
    
    return repo.update(brand_id, update_data, updated_by=updated_by)


def _slugify(value: str) -> str:
    return slugify(value or "", lowercase=True) or "n-a"


def _make_unique_slug(db: Session, model, base: str, exclude_id: Optional[str] = None) -> str:
    # if exact base exists (excluding optional id), find suffix
    exists = db.query(model).filter(model.slug == base)
    if exclude_id:
        exists = exists.filter(model.id != exclude_id)
    if exists.first():
        # find max suffix
        like_pattern = f"{base}-%"
        rows = db.query(model.slug).filter(model.slug.ilike(like_pattern)).all()
        suffixes = [int(r[0].rsplit("-", 1)[1]) for r in rows if r[0].rsplit("-", 1)[-1].isdigit()]
        next_suffix = (max(suffixes) + 1) if suffixes else 2
        return f"{base}-{next_suffix}"
    return base


def soft_delete_brand(db: Session, brand_id: str, deleted_by: Optional[str] = None) -> bool:
    repo = BrandRepository(db)
    return repo.delete(brand_id, deleted_by=deleted_by)
