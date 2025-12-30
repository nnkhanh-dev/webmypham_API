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

router = APIRouter(prefix="/carts", tags=["carts"])


@router.post("/", response_model=BaseResponse[CartResponse], status_code=status.HTTP_201_CREATED)
def create_cart_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    obj = create_cart_for_user(db, str(current_user.id), created_by=str(current_user.id))
    return BaseResponse(success=True, message="Created", data=obj)


@router.get("/me", response_model=BaseResponse[CartResponse])
def get_my_cart(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    obj = get_cart_by_user(db, str(current_user.id))
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return BaseResponse(success=True, message="OK", data=obj)


@router.post("/{cart_id}/items", response_model=BaseResponse[CartItemResponse], status_code=status.HTTP_201_CREATED)
def add_item(cart_id: str, item_in: CartItemCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    obj = add_cart_item(db, cart_id, item_in, created_by=str(current_user.id))
    return BaseResponse(success=True, message="Created", data=obj)


@router.put("/{cart_id}/items/{item_id}", response_model=BaseResponse[CartItemResponse])
def update_item(cart_id: str, item_id: str, item_in: CartItemUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    obj = update_cart_item(db, item_id, item_in, updated_by=str(current_user.id))
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return BaseResponse(success=True, message="Updated", data=obj)


@router.delete("/{cart_id}/items/{item_id}", response_model=BaseResponse[None])
def delete_item(cart_id: str, item_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    obj = get_cart_item(db, item_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    ok = delete_cart_item(db, item_id, deleted_by=str(current_user.id))
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return BaseResponse(success=True, message="Deleted", data=None)
