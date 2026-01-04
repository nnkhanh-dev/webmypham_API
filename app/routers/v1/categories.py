from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.pagination import get_pagination
from app.dependencies.permission import require_roles
from app.schemas.request.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.response.base import BaseResponse
from app.services.category_service import (
    get_category,
    get_categories,
    create_category,
    update_category,
    delete_category,
    get_category_children,
    get_category_tree,
)

router = APIRouter()


@router.get("/", response_model=BaseResponse[List[CategoryResponse]])
def list_categories(params: dict = Depends(get_pagination), db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
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


@router.get("/tree", response_model=BaseResponse[List[CategoryResponse]])
def category_tree(db: Session = Depends(get_db)):
    items = get_category_tree(db, max_depth=3)
    return BaseResponse(success=True, message="Lấy cây danh mục thành công.", data=items)


@router.get("/{category_id}", response_model=BaseResponse[CategoryResponse])
def read_category(category_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
    obj = get_category(db, category_id)
    if not obj:
        return BaseResponse(success=False, message="Không tìm thấy danh mục.", data=None)
    return BaseResponse(success=True, message="Lấy danh mục thành công.", data=obj)


@router.post("/", response_model=BaseResponse[CategoryResponse], status_code=status.HTTP_201_CREATED)
def create_category_endpoint(category_in: CategoryCreate, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
    try:
        obj = create_category(db, category_in, created_by=str(current_user.id) if current_user else None)
    except ValueError as e:
        return BaseResponse(success=False, message=str(e), data=None)
    return BaseResponse(success=True, message="Danh mục đã được tạo.", data=obj)


@router.put("/{category_id}", response_model=BaseResponse[CategoryResponse])
def update_category_endpoint(category_id: str, category_in: CategoryUpdate, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
    obj = update_category(db, category_id, category_in, updated_by=str(current_user.id) if current_user else None)
    if not obj:
        return BaseResponse(success=False, message="Không tìm thấy danh mục.", data=None)
    return BaseResponse(success=True, message="Danh mục đã được cập nhật.", data=obj)


@router.delete("/{category_id}", response_model=BaseResponse[None])
def delete_category_endpoint(category_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
    ok = delete_category(db, category_id, deleted_by=str(current_user.id) if current_user else None)
    if not ok:
        return BaseResponse(success=False, message="Không tìm thấy danh mục.", data=None)
    return BaseResponse(success=True, message="Danh mục đã được xóa.", data=None)


@router.get("/{category_id}/children", response_model=BaseResponse[List[CategoryResponse]])
def list_children(category_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
    items = get_category_children(db, category_id)
    return BaseResponse(success=True, message="Lấy danh sách danh mục con thành công.", data=items)
