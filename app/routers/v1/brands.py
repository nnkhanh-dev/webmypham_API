from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.pagination import get_pagination
from app.dependencies.permission import require_roles
from app.schemas.request.brand import BrandResponse
from app.schemas.response.base import BaseResponse
from app.services.brand_service import (
    get_brand,
    get_brand_by_name,
    get_brands,
    create_brand_with_image,
    update_brand_with_image,
    soft_delete_brand,
)

router = APIRouter()


@router.get("/", response_model=BaseResponse[List[BrandResponse]])
def list_brands(
    params: dict = Depends(get_pagination),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("CLIENT", "ADMIN")),
):
    items, total = get_brands(
        db,
        skip=params.get("skip", 0),
        limit=params.get("limit", 100),
        q=params.get("q"),
        sort_by=params.get("sort_by", "id"),
        sort_dir=params.get("sort_dir", "desc"),
    )
    meta = {**params, "total": total}
    return BaseResponse(success=True, message="OK", data=items, meta=meta)


@router.get("/{brand_id}", response_model=BaseResponse[BrandResponse])
def read_brand(brand_id: str, db: Session = Depends(get_db)):
    obj = get_brand(db, brand_id)
    if not obj:
        return BaseResponse(success=False, message="Không tìm thấy thương hiệu.", data=None)
    return BaseResponse(success=True, message="Lấy thương hiệu thành công.", data=obj)


@router.post("/", response_model=BaseResponse[BrandResponse], status_code=status.HTTP_201_CREATED)
async def create_brand_endpoint(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("ADMIN")),
):
    """
    Tạo brand mới với upload ảnh trực tiếp
    - name: Tên thương hiệu (required)
    - description: Mô tả
    - image: File ảnh (optional)
    """
    if get_brand_by_name(db, name):
        return BaseResponse(success=False, message="Tên thương hiệu đã tồn tại.", data=None)
    
    obj = await create_brand_with_image(
        db, 
        name=name,
        description=description,
        image_file=image,
        created_by=str(current_user.id) if current_user else None
    )
    return BaseResponse(success=True, message="Thương hiệu đã được tạo.", data=obj)


@router.put("/{brand_id}", response_model=BaseResponse[BrandResponse])
async def update_brand_endpoint(
    brand_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("ADMIN")),
):
    """
    Cập nhật brand với upload ảnh trực tiếp
    - name: Tên thương hiệu
    - description: Mô tả
    - image: File ảnh mới (optional, nếu có sẽ thay thế ảnh cũ)
    """
    obj = await update_brand_with_image(
        db,
        brand_id=brand_id,
        name=name,
        description=description,
        image_file=image,
        updated_by=str(current_user.id) if current_user else None
    )
    if not obj:
        return BaseResponse(success=False, message="Không tìm thấy thương hiệu.", data=None)
    return BaseResponse(success=True, message="Thương hiệu đã được cập nhật.", data=obj)


@router.delete("/{brand_id}", response_model=BaseResponse[None])
def delete_brand_endpoint(brand_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN")),):
    ok = soft_delete_brand(db, brand_id, deleted_by=str(current_user.id) if current_user else None)
    if not ok:
        return BaseResponse(success=False, message="Không tìm thấy thương hiệu.", data=None)
    return BaseResponse(success=True, message="Thương hiệu đã được xóa.", data=None)
