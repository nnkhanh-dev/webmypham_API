from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.pagination import get_pagination
from app.dependencies.permission import require_roles
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.response.base import BaseResponse
from app.services.category_service import (
    get_category,
    get_categories,
    create_category,
    update_category,
    delete_category,
    get_category_children,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=BaseResponse[List[CategoryResponse]])
def list_categories(params: dict = Depends(get_pagination), db: Session = Depends(get_db)):
    items, total = get_categories(
        db,
        skip=params.get("skip", 0),
        limit=params.get("limit", 100),
        q=params.get("q"),
        sort_by=params.get("sort_by", "id"),
        sort_dir=params.get("sort_dir", "desc"),
    )
    meta = {**params, "total": total}
    return BaseResponse(success=True, message="OK", data=items, meta=meta)


@router.get("/{category_id}", response_model=BaseResponse[CategoryResponse])
def read_category(category_id: str, db: Session = Depends(get_db)):
    obj = get_category(db, category_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return BaseResponse(success=True, message="OK", data=obj)


@router.post("/", response_model=BaseResponse[CategoryResponse], status_code=status.HTTP_201_CREATED)
def create_category_endpoint(category_in: CategoryCreate, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
    obj = create_category(db, category_in, created_by=str(current_user.id) if current_user else None)
    return BaseResponse(success=True, message="Created", data=obj)


@router.put("/{category_id}", response_model=BaseResponse[CategoryResponse])
def update_category_endpoint(category_id: str, category_in: CategoryUpdate, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
    obj = update_category(db, category_id, category_in, updated_by=str(current_user.id) if current_user else None)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return BaseResponse(success=True, message="Updated", data=obj)


@router.delete("/{category_id}", response_model=BaseResponse[None])
def delete_category_endpoint(category_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
    ok = delete_category(db, category_id, deleted_by=str(current_user.id) if current_user else None)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return BaseResponse(success=True, message="Deleted", data=None)


@router.get("/{category_id}/children", response_model=BaseResponse[List[CategoryResponse]])
def list_children(category_id: str, db: Session = Depends(get_db)):
    items = get_category_children(db, category_id)
    return BaseResponse(success=True, message="OK", data=items)
