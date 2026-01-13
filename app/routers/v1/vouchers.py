from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.permission import require_roles
from app.schemas.request.voucher import VoucherCreate, VoucherUpdate, VoucherResponse
from app.schemas.response.base import BaseResponse
from app.schemas.response.pagination import PaginatedResponse
from app.services.voucher_service import (
    get_voucher,
    get_voucher_by_code,
    get_vouchers,
    create_voucher,
    update_voucher,
    soft_delete_voucher,
)

router = APIRouter()


class VoucherPaginatedResponse(PaginatedResponse[VoucherResponse]):
    """Paginated response for vouchers"""
    pass


@router.get("/", response_model=BaseResponse[VoucherPaginatedResponse])
def list_vouchers(
    skip: int = Query(0, ge=0, description="Số lượng bỏ qua"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng lấy"),
    q: Optional[str] = Query(None, description="Tìm kiếm theo mã hoặc mô tả"),
    min_discount: Optional[float] = Query(None, ge=0, description="Giảm giá tối thiểu (%)"),
    max_discount: Optional[float] = Query(None, le=100, description="Giảm giá tối đa (%)"),
    sort_by: str = Query("created_at", description="Sắp xếp theo: id, code, discount, quantity, created_at"),
    sort_dir: str = Query("desc", description="Thứ tự: asc, desc"),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("CLIENT", "ADMIN")),
):
    """
    Lấy danh sách vouchers với phân trang và tìm kiếm
    
    - **skip**: Số lượng bỏ qua (phân trang)
    - **limit**: Số lượng lấy tối đa
    - **q**: Tìm kiếm theo mã hoặc mô tả
    - **min_discount**: Lọc theo giảm giá tối thiểu (%)
    - **max_discount**: Lọc theo giảm giá tối đa (%)
    - **sort_by**: Sắp xếp theo field
    - **sort_dir**: Thứ tự sắp xếp (asc/desc)
    """
    items, total = get_vouchers(
        db,
        skip=skip,
        limit=limit,
        q=q,
        min_discount=min_discount,
        max_discount=max_discount,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    
    # Filter vouchers by limit (only show vouchers user can still use)
    from app.models.order import Order
    filtered_items = []
    for voucher in items:
        # Check if voucher has limit
        if voucher.limit:
            # Count how many times current user has used this voucher
            usage_count = db.query(Order).filter(
                Order.voucher_id == voucher.id,
                Order.user_id == current_user.id,
                Order.status != 'cancelled',
                Order.deleted_at.is_(None)
            ).count()
            
            # Only include if user hasn't reached limit
            if usage_count < voucher.limit:
                filtered_items.append(voucher)
        else:
            # No limit, always include
            filtered_items.append(voucher)
    
    items = filtered_items
    total = len(filtered_items)
    
    paginated_data = VoucherPaginatedResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )
    
    return BaseResponse(success=True, message="Lấy danh sách voucher thành công.", data=paginated_data)


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
    # Kiểm tra voucher tồn tại
    existing = get_voucher(db, voucher_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher not found")
    
    # Kiểm tra duplicate code nếu đang thay đổi code
    if voucher_in.code and voucher_in.code.upper() != existing.code:
        duplicate = get_voucher_by_code(db, voucher_in.code)
        if duplicate and duplicate.id != voucher_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Voucher code '{voucher_in.code.upper()}' already exists"
            )
    
    obj = update_voucher(db, voucher_id, voucher_in, updated_by=str(current_user.id) if current_user else None)
    return BaseResponse(success=True, message="Updated", data=obj)

@router.delete("/{voucher_id}", response_model=BaseResponse[None])
def delete_voucher_endpoint(voucher_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN")),):
    ok = soft_delete_voucher(db, voucher_id, deleted_by=str(current_user.id) if current_user else None)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher not found")
    return BaseResponse(success=True, message="Deleted", data=None)