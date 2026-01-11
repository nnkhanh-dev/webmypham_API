from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.request.wishlist import (
    WishlistResponse,
    WishlistItemCreate,
    WishlistItemResponse,
)
from app.schemas.response.base import BaseResponse
from app.services.wishlist_service import (
    create_wishlist_for_user,
    get_wishlist_by_user,
    add_wishlist_item,
    list_wishlist_items,
    remove_wishlist_item,
    get_wishlist_item,
)
from app.repositories.wishlist_repository import WishlistRepository
from app.repositories.product_type_repository import ProductTypeRepository

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=BaseResponse[WishlistResponse], status_code=status.HTTP_201_CREATED)
def create_wishlist(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """Create or get wishlist for current user (idempotent)"""
    try:
        obj = create_wishlist_for_user(
            db, 
            str(current_user.id), 
            created_by=str(current_user.id)
        )
        return BaseResponse(
            success=True, 
            message="Danh sách yêu thích đã được tạo.", 
            data=obj
        )
    except Exception as e:
        logger.error(f"Error creating wishlist for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi tạo danh sách yêu thích"
        )


@router.get("/me", response_model=BaseResponse[WishlistResponse])
def get_my_wishlist(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """Get current user's wishlist"""
    obj = get_wishlist_by_user(db, str(current_user.id))
    if not obj:
        return BaseResponse(
            success=False, 
            message="Không tìm thấy danh sách yêu thích.", 
            data=None
        )
    return BaseResponse(
        success=True, 
        message="Lấy danh sách yêu thích thành công.", 
        data=obj
    )


@router.post(
    "/{wishlist_id}/items", 
    response_model=BaseResponse[WishlistItemResponse], 
    status_code=status.HTTP_201_CREATED
)
def add_item(
    wishlist_id: str, 
    item_in: WishlistItemCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """Add item to wishlist"""
    # Validate wishlist exists and belongs to current user
    repo = WishlistRepository(db)
    wishlist = repo.get(wishlist_id)
    
    if not wishlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy danh sách yêu thích"
        )
    
    if str(wishlist.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập vào danh sách này"
        )
    
    # Validate product exists
    pt_repo = ProductTypeRepository(db)
    pt = pt_repo.get(item_in.product_type_id)
    
    if not pt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sản phẩm"
        )
    
    # Add item (service will check for duplicates)
    try:
        obj = add_wishlist_item(
            db, 
            wishlist_id, 
            item_in, 
            created_by=str(current_user.id)
        )
        return BaseResponse(
            success=True, 
            message="Sản phẩm đã được thêm vào danh sách yêu thích.", 
            data=obj
        )
    except ValueError as e:
        # Duplicate item
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding item to wishlist {wishlist_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi thêm sản phẩm"
        )


@router.get(
    "/{wishlist_id}/items", 
    response_model=BaseResponse[List[WishlistItemResponse]]
)
def list_items(
    wishlist_id: str, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get items in wishlist (with authorization check)"""
    # SECURITY FIX: Add authorization check
    repo = WishlistRepository(db)
    wishlist = repo.get(wishlist_id)
    
    if not wishlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy danh sách yêu thích"
        )
    
    if str(wishlist.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập vào danh sách này"
        )
    
    items, total = list_wishlist_items(db, wishlist_id)
    meta = {"total": total}
    return BaseResponse(
        success=True, 
        message="Lấy danh sách sản phẩm yêu thích thành công.", 
        data=items, 
        meta=meta
    )


@router.delete("/{wishlist_id}/items/{item_id}", response_model=BaseResponse[None])
def delete_item(
    wishlist_id: str,
    item_id: str, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """Delete item from wishlist"""
    # Get item
    obj = get_wishlist_item(db, item_id)
    
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sản phẩm trong danh sách yêu thích"
        )
    
    # Verify item belongs to specified wishlist
    if obj.wishlist_id != wishlist_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sản phẩm trong danh sách yêu thích"
        )
    
    # Check authorization: item's wishlist must belong to current user
    repo = WishlistRepository(db)
    wishlist = repo.get(wishlist_id)
    
    if not wishlist or str(wishlist.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa sản phẩm này"
        )
    
    # Delete item
    ok = remove_wishlist_item(db, item_id, deleted_by=str(current_user.id))
    
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xóa sản phẩm"
        )
    
    return BaseResponse(
        success=True, 
        message="Sản phẩm trong danh sách yêu thích đã được xóa.", 
        data=None
    )
