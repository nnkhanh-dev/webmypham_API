from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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

router = APIRouter(prefix="/wishlists", tags=["wishlists"])


@router.post("/", response_model=BaseResponse[WishlistResponse], status_code=status.HTTP_201_CREATED)
def create_wishlist(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        obj = create_wishlist_for_user(db, str(current_user.id), created_by=str(current_user.id))
        return BaseResponse(success=True, message="Danh sách yêu thích đã được tạo.", data=obj)
    except Exception:
        return BaseResponse(success=False, message="Đã xảy ra lỗi.", data=None)


@router.get("/me", response_model=BaseResponse[WishlistResponse])
def get_my_wishlist(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    obj = get_wishlist_by_user(db, str(current_user.id))
    if not obj:
        return BaseResponse(success=False, message="Không tìm thấy danh sách yêu thích.", data=None)
    return BaseResponse(success=True, message="Lấy danh sách yêu thích thành công.", data=obj)


@router.post("/{wishlist_id}/items", response_model=BaseResponse[WishlistItemResponse], status_code=status.HTTP_201_CREATED)
def add_item(wishlist_id: str, item_in: WishlistItemCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        # ensure wishlist exists and belongs to current user
        repo = WishlistRepository(db)
        wishlist = repo.get(wishlist_id)
        if not wishlist:
            return BaseResponse(success=False, message="Không tìm thấy danh sách yêu thích.", data=None)
        if str(wishlist.user_id) != str(current_user.id):
            return BaseResponse(success=False, message="Bạn không có quyền truy cập vào danh sách này.", data=None)
        # validate product exists for clearer message
        from app.models.productType import ProductType
        pt = db.query(ProductType).filter(ProductType.id == item_in.product_type_id, ProductType.deleted_at.is_(None)).first()
        if not pt:
            return BaseResponse(success=False, message="Không tìm thấy sản phẩm.", data=None)

        obj = add_wishlist_item(db, wishlist_id, item_in, created_by=str(current_user.id))
        return BaseResponse(success=True, message="Sản phẩm đã được thêm vào danh sách yêu thích.", data=obj)
    except HTTPException as e:
        code = getattr(e, "status_code", None)
        detail = getattr(e, "detail", "")
        if code == status.HTTP_404_NOT_FOUND:
            return BaseResponse(success=False, message="Không tìm thấy sản phẩm: {detail}.", data=None)
        elif code == status.HTTP_400_BAD_REQUEST:
            return BaseResponse(success=False, message="Yêu cầu không hợp lệ: {detail}.", data=None)
        else:
            return BaseResponse(success=False, message="Đã xảy ra lỗi: {detail}.", data=None)
    except Exception:
        return BaseResponse(success=False, message="Đã xảy ra lỗi.", data=None)


@router.get("/{wishlist_id}/items", response_model=BaseResponse[List[WishlistItemResponse]])
def list_items(wishlist_id: str, db: Session = Depends(get_db)):
    items, total = list_wishlist_items(db, wishlist_id)
    meta = {"total": total}
    return BaseResponse(success=True, message="Lấy danh sách sản phẩm yêu thích thành công.", data=items, meta=meta)


@router.delete("/{wishlist_id}/items/{item_id}", response_model=BaseResponse[None])
def delete_item(wishlist_id: str, item_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    obj = get_wishlist_item(db, item_id)
    if not obj or obj.wishlist_id != wishlist_id:
        return BaseResponse(success=False, message="Không tìm thấy sản phẩm trong danh sách yêu thích.", data=None)
    ok = remove_wishlist_item(db, item_id, deleted_by=str(current_user.id))
    if not ok:
        return BaseResponse(success=False, message="Không tìm thấy sản phẩm trong danh sách yêu thích.", data=None)
    return BaseResponse(success=True, message="Sản phẩm trong danh sách yêu thích đã được xóa.", data=None) 