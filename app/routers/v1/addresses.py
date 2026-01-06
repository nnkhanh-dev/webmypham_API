from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.pagination import get_pagination
from app.schemas.request.address import AddressCreate, AddressUpdate
from app.schemas.response.address import AddressResponse
from app.schemas.response.base import BaseResponse
from app.services.address_service import (
    create_address,
    get_address,
    list_addresses,
    update_address,
    delete_address,
    set_default_address,
)

router = APIRouter()


@router.post("/", response_model=BaseResponse[AddressResponse], response_model_exclude_none=True, status_code=status.HTTP_201_CREATED)
async def create_address_endpoint(
    address_in: AddressCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Tạo địa chỉ mới"""
    try:
        obj = await create_address(db, str(current_user.id), address_in, created_by=str(current_user.id))
        return BaseResponse(success=True, message="Địa chỉ đã được tạo.", data=obj)
    except HTTPException:
        raise
    except Exception as e:
        return BaseResponse(success=False, message=f"Đã xảy ra lỗi: {str(e)}", data=None)


@router.get("/", response_model=BaseResponse[List[AddressResponse]], response_model_exclude_none=True)
def list_addresses_endpoint(
    params: dict = Depends(get_pagination),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lấy danh sách địa chỉ của user"""
    items, total = list_addresses(
        db,
        str(current_user.id),
        skip=params.get("skip", 0),
        limit=params.get("limit", 100)
    )
    meta = {**params, "total": total}
    return BaseResponse(success=True, message="OK", data=items, meta=meta)


@router.get("/{address_id}", response_model=BaseResponse[AddressResponse], response_model_exclude_none=True)
def get_address_endpoint(
    address_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lấy một địa chỉ theo ID"""
    try:
        obj = get_address(db, address_id, str(current_user.id))
        return BaseResponse(success=True, message="OK", data=obj)
    except HTTPException:
        raise


@router.put("/{address_id}", response_model=BaseResponse[AddressResponse], response_model_exclude_none=True)
async def update_address_endpoint(
    address_id: str,
    address_in: AddressUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cập nhật địa chỉ"""
    try:
        obj = await update_address(db, address_id, str(current_user.id), address_in, updated_by=str(current_user.id))
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy địa chỉ.")
        return BaseResponse(success=True, message="Địa chỉ đã được cập nhật.", data=obj)
    except HTTPException:
        raise
    except Exception as e:
        return BaseResponse(success=False, message=f"Đã xảy ra lỗi: {str(e)}", data=None)


@router.delete("/{address_id}", response_model=BaseResponse[None], response_model_exclude_none=True)
def delete_address_endpoint(
    address_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Xóa địa chỉ"""
    try:
        ok = delete_address(db, address_id, str(current_user.id), deleted_by=str(current_user.id))
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy địa chỉ.")
        return BaseResponse(success=True, message="Địa chỉ đã được xóa.", data=None)
    except HTTPException:
        raise
    except Exception as e:
        return BaseResponse(success=False, message=f"Đã xảy ra lỗi: {str(e)}", data=None)


@router.patch("/{address_id}/set-default", response_model=BaseResponse[AddressResponse], response_model_exclude_none=True)
def set_default_address_endpoint(
    address_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Đặt địa chỉ làm mặc định"""
    try:
        obj = set_default_address(db, address_id, str(current_user.id), updated_by=str(current_user.id))
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy địa chỉ.")
        return BaseResponse(success=True, message="Đã đặt làm địa chỉ mặc định.", data=obj)
    except HTTPException:
        raise
    except Exception as e:
        return BaseResponse(success=False, message=f"Đã xảy ra lỗi: {str(e)}", data=None)

