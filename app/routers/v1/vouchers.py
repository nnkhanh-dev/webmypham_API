from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.pagination import get_pagination
from app.dependencies.permission import require_roles
from app.schemas.request.voucher import VoucherCreate, VoucherUpdate, VoucherResponse
from app.schemas.response.base import BaseResponse
from app.services.voucher_service import (
    get_voucher,
    get_voucher_by_code,
    get_vouchers,
    create_voucher,
    update_voucher,
    soft_delete_voucher,
)

router = APIRouter()

@router.get("/", response_model=BaseResponse[List[VoucherResponse]])
def list_vouchers(
    params: dict = Depends(get_pagination),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("CLIENT", "ADMIN")),
):
    items, total = get_vouchers(
        db,
        skip=params.get("skip", 0),
        limit=params.get("limit", 100),
        q=params.get("q"),
        min_discount=params.get("min_discount"),
        max_discount=params.get("max_discount"),
        sort_by=params.get("sort_by", "id"),
        sort_dir=params.get("sort_dir", "desc"),
    )
    meta = {**params, "total": total}
    return BaseResponse(success=True, message="OK", data=items, meta=meta)

@router.get("/{voucher_id}", response_model=BaseResponse[VoucherResponse])
def read_voucher(voucher_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles("CLIENT", "ADMIN"))):
    obj = get_voucher(db, voucher_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher not found")
    return BaseResponse(success=True, message="OK", data=obj)

@router.post("/", response_model=BaseResponse[VoucherResponse], status_code=status.HTTP_201_CREATED)
def create_voucher_endpoint(voucher_in: VoucherCreate, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN")),):
    if get_voucher_by_code(db, voucher_in.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Voucher code already exists")
    obj = create_voucher(db, voucher_in, created_by=str(current_user.id) if current_user else None)
    return BaseResponse(success=True, message="Created", data=obj)

@router.put("/{voucher_id}", response_model=BaseResponse[VoucherResponse])
def update_voucher_endpoint(voucher_id: str, voucher_in: VoucherUpdate, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN")),):
    obj = update_voucher(db, voucher_id, voucher_in, updated_by=str(current_user.id) if current_user else None)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher not found")
    return BaseResponse(success=True, message="Updated", data=obj)

@router.delete("/{voucher_id}", response_model=BaseResponse[None])
def delete_voucher_endpoint(voucher_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN")),):
    ok = soft_delete_voucher(db, voucher_id, deleted_by=str(current_user.id) if current_user else None)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher not found")
    return BaseResponse(success=True, message="Deleted", data=None)