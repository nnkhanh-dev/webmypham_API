from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.request.cart import (
    CartCreate,
    CartResponse,
    CartItemCreate,
    CartItemResponse,
    CartItemUpdate,
)
from app.schemas.response.base import BaseResponse
from app.schemas.response.cart import CartFullResponse, CartItemFullResponse
from app.services.cart_service import (
    create_cart_for_user,
    get_cart_by_user,
    get_cart,
    add_cart_item,
    list_cart_items,
    update_cart_item,
    delete_cart_item,
    get_cart_item,
)
from app.models.productType import ProductType
from app.models.cartItem import CartItem

router = APIRouter()


@router.post("/", response_model=BaseResponse[CartResponse], status_code=status.HTTP_201_CREATED)
def create_cart_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        obj = create_cart_for_user(db, str(current_user.id), created_by=str(current_user.id))
        return BaseResponse(success=True, message="Giỏ hàng đã được tạo.", data=obj)
    except Exception:
        return BaseResponse(success=False, message="Đã xảy ra lỗi.", data=None)


@router.get("/me", response_model=BaseResponse[CartFullResponse])
def get_my_cart(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Lấy giỏ hàng với đầy đủ thông tin sản phẩm (tên, giá, hình, biến thể)"""
    obj = get_cart_by_user(db, str(current_user.id))
    if not obj:
        return BaseResponse(success=False, message="Không tìm thấy giỏ hàng.", data=None)
    
    # Filter out deleted items
    if obj.items:
        obj.items = [item for item in obj.items if item.deleted_at is None]
    
    return BaseResponse(success=True, message="Lấy giỏ hàng thành công.", data=obj)


@router.post("/items", response_model=BaseResponse[CartItemResponse], status_code=status.HTTP_201_CREATED)
def add_item_auto(item_in: CartItemCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Thêm sản phẩm vào giỏ hàng.
    Tự động tìm hoặc tạo giỏ hàng cho user nếu chưa có.
    Sử dụng endpoint này khi add từ trang home/product detail.
    """
    try:
        # Tìm cart của user, nếu chưa có thì tạo mới
        cart = get_cart_by_user(db, str(current_user.id))
        if not cart:
            cart = create_cart_for_user(db, str(current_user.id), created_by=str(current_user.id))
        
        cart_id = cart.id
        
        # validate product type and stock
        pt = db.query(ProductType).filter(ProductType.id == item_in.product_type_id, ProductType.deleted_at.is_(None)).first()
        if not pt:
            return BaseResponse(success=False, message="Không tìm thấy sản phẩm.", data=None)
        
        existing = db.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.product_type_id == item_in.product_type_id, CartItem.deleted_at.is_(None)).first()
        total_requested = (existing.quantity if existing else 0) + int(item_in.quantity)
        if pt.stock is not None and total_requested > pt.stock:
            return BaseResponse(success=False, message=f"Không đủ tồn kho: yêu cầu {total_requested}, còn {pt.stock}.", data=None)
        
        obj = add_cart_item(db, cart_id, item_in, created_by=str(current_user.id))
        return BaseResponse(success=True, message="Sản phẩm đã được thêm vào giỏ hàng.", data=obj)
    except Exception as e:
        return BaseResponse(success=False, message=f"Đã xảy ra lỗi: {str(e)}", data=None)


@router.post("/{cart_id}/items", response_model=BaseResponse[CartItemResponse], status_code=status.HTTP_201_CREATED)
def add_item(cart_id: str, item_in: CartItemCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        # ensure cart exists and belongs to current user
        cart = get_cart(db, cart_id)
        if not cart:
            return BaseResponse(success=False, message=f"Không tìm thấy giỏ hàng.", data=None)
        if str(cart.user_id) != str(current_user.id):
            return BaseResponse(success=False, message="Bạn không có quyền truy cập vào giỏ hàng này.", data=None)
        # validate product type and stock with details
        pt = db.query(ProductType).filter(ProductType.id == item_in.product_type_id, ProductType.deleted_at.is_(None)).first()
        if not pt:
            return BaseResponse(success=False, message=f"Không tìm thấy sản phẩm.", data=None)
        existing = db.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.product_type_id == item_in.product_type_id, CartItem.deleted_at.is_(None)).first()
        total_requested = (existing.quantity if existing else 0) + int(item_in.quantity)
        if pt.stock is not None and total_requested > pt.stock:
            return BaseResponse(success=False, message=f"Không đủ tồn kho: yêu cầu {total_requested}, còn {pt.stock}.", data=None)
        obj = add_cart_item(db, cart_id, item_in, created_by=str(current_user.id))
        return BaseResponse(success=True, message="Sản phẩm đã được thêm vào giỏ hàng.", data=obj)
    except HTTPException as e:
        code = getattr(e, "status_code", None)
        # use exception detail if available, translate common phrases
        detail = getattr(e, "detail", "lỗi")
        if code == status.HTTP_404_NOT_FOUND:
            return BaseResponse(success=False, message=f"Không tìm thấy sản phẩm: {detail}.", data=None)
        elif code == status.HTTP_400_BAD_REQUEST:
            return BaseResponse(success=False, message=f"Không đủ tồn kho: {detail}.", data=None)
        else:
            return BaseResponse(success=False, message=f"Đã xảy ra lỗi: {detail}.", data=None)
    except Exception:
        return BaseResponse(success=False, message="Đã xảy ra lỗi.", data=None)


@router.put("/{cart_id}/items/{item_id}", response_model=BaseResponse[CartItemResponse])
def update_item(cart_id: str, item_id: str, item_in: CartItemUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        # ensure cart belongs to current user
        cart = get_cart(db, cart_id)
        if not cart:
            return BaseResponse(success=False, message="Không tìm thấy giỏ hàng.", data=None)
        if str(cart.user_id) != str(current_user.id):
            return BaseResponse(success=False, message="Bạn không có quyền truy cập vào giỏ hàng này.", data=None)
        
        # ensure item exists and belongs to the cart
        existing = get_cart_item(db, item_id)
        if not existing:
            return BaseResponse(success=False, message="Không tìm thấy sản phẩm trong giỏ hàng.", data=None)
        if existing.cart_id != cart_id:
            return BaseResponse(success=False, message="Sản phẩm không thuộc giỏ hàng này.", data=None)

        # if updating product_type_id, validate the new product type exists
        if item_in.product_type_id is not None:
            pt = db.query(ProductType).filter(
                ProductType.id == item_in.product_type_id, 
                ProductType.deleted_at.is_(None)
            ).first()
            if not pt:
                return BaseResponse(success=False, message="Không tìm thấy biến thể sản phẩm mới.", data=None)
            
            # check stock for new variant
            new_qty = item_in.quantity if item_in.quantity is not None else existing.quantity
            if pt.stock is not None and new_qty > pt.stock:
                return BaseResponse(
                    success=False, 
                    message=f"Không đủ tồn kho cho biến thể mới: yêu cầu {new_qty}, còn {pt.stock}.", 
                    data=None
                )
        
        # if only updating quantity, check stock of current product type
        elif item_in.quantity is not None:
            pt = db.query(ProductType).filter(
                ProductType.id == existing.product_type_id, 
                ProductType.deleted_at.is_(None)
            ).first()
            if not pt:
                return BaseResponse(success=False, message="Không tìm thấy sản phẩm.", data=None)
            new_qty = int(item_in.quantity)
            if pt.stock is not None and new_qty > pt.stock:
                return BaseResponse(
                    success=False, 
                    message=f"Không đủ tồn kho: yêu cầu {new_qty}, còn {pt.stock}.", 
                    data=None
                )

        obj = update_cart_item(db, item_id, item_in, updated_by=str(current_user.id))
        if not obj:
            return BaseResponse(success=False, message="Không tìm thấy sản phẩm trong giỏ hàng.", data=None)
        return BaseResponse(success=True, message="Sản phẩm trong giỏ hàng đã được cập nhật.", data=obj)
    except HTTPException as e:
        detail = getattr(e, "detail", "")
        if "not found" in detail.lower():
            return BaseResponse(success=False, message="Không tìm thấy sản phẩm hoặc biến thể.", data=None)
        elif "Không đủ tồn kho" in detail or "insufficient stock" in detail.lower():
            return BaseResponse(success=False, message=detail, data=None)
        else:
            return BaseResponse(success=False, message=f"Đã xảy ra lỗi: {detail}.", data=None)
    except Exception:
        return BaseResponse(success=False, message="Đã xảy ra lỗi.", data=None)


@router.delete("/{cart_id}/items/{item_id}", response_model=BaseResponse[None])
def delete_item(cart_id: str, item_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    obj = get_cart_item(db, item_id)
    if not obj:
        return BaseResponse(success=False, message=f"Không tìm thấy sản phẩm trong giỏ hàng.", data=None)
    if obj.cart_id != cart_id:
        return BaseResponse(success=False, message="Sản phẩm không thuộc giỏ hàng này.", data=None)
    ok = delete_cart_item(db, item_id, deleted_by=str(current_user.id))
    if not ok:
        return BaseResponse(success=False, message=f"Không tìm thấy sản phẩm trong giỏ hàng.", data=None)
    return BaseResponse(success=True, message="Sản phẩm trong giỏ hàng đã được xóa.", data=None)