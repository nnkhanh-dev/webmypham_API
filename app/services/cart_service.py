from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from app.models.cart import Cart
from app.models.cartItem import CartItem
from app.models.productType import ProductType
from app.repositories.cart_repository import CartRepository, CartItemRepository
from app.schemas.request.cart import CartItemCreate, CartItemUpdate
from fastapi import HTTPException, status


def get_cart_by_user(db: Session, user_id: str) -> Optional[Cart]:
    repo = CartRepository(db)
    return repo.get_by_user(user_id)


def create_cart_for_user(db: Session, user_id: str, created_by: Optional[str] = None) -> Cart:
    repo = CartRepository(db)
    existing = repo.get_by_user(user_id)
    if existing:
        return existing
    data = {"user_id": user_id}
    return repo.create(data, created_by=created_by)


def get_cart(db: Session, cart_id: str) -> Optional[Cart]:
    repo = CartRepository(db)
    return repo.get(cart_id)


def add_cart_item(db: Session, cart_id: str, item_in: CartItemCreate, created_by: Optional[str] = None) -> CartItem:
    repo = CartItemRepository(db)
    data = item_in.dict()
    data["cart_id"] = cart_id
    # check product type stock
    product_type = db.query(ProductType).filter(ProductType.id == data["product_type_id"], ProductType.deleted_at.is_(None)).first()
    if not product_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product type not found")

    # if existing cart item exists, ensure total quantity <= stock
    existing = repo.get_by_cart_and_product(cart_id, data["product_type_id"])
    requested_qty = int(data.get("quantity", 0))
    existing_qty = existing.quantity if existing else 0
    total_qty = existing_qty + requested_qty
    if product_type.stock is not None and total_qty > product_type.stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock for requested quantity")

    # if existing, update quantity, else create
    if existing:
        return repo.update(existing.id, {"quantity": total_qty}, updated_by=created_by)

    return repo.create(data, created_by=created_by)


def list_cart_items(db: Session, cart_id: str, skip: int = 0, limit: int = 100) -> Tuple[List[CartItem], int]:
    repo = CartItemRepository(db)
    return repo.list_by_cart(cart_id, skip=skip, limit=limit)


def update_cart_item(db: Session, item_id: str, item_in: CartItemUpdate, updated_by: Optional[str] = None) -> Optional[CartItem]:
    repo = CartItemRepository(db)
    data = item_in.dict(exclude_unset=True)
    # if updating quantity, validate against product type stock
    if "quantity" in data:
        item = repo.get(item_id)
        if not item:
            return None
        product_type = db.query(ProductType).filter(ProductType.id == item.product_type_id, ProductType.deleted_at.is_(None)).first()
        if not product_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product type not found")
        new_qty = int(data["quantity"])
        if product_type.stock is not None and new_qty > product_type.stock:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock for requested quantity")

    return repo.update(item_id, data, updated_by=updated_by)


def delete_cart_item(db: Session, item_id: str, deleted_by: Optional[str] = None) -> bool:
    repo = CartItemRepository(db)
    return repo.delete(item_id, deleted_by=deleted_by)


def get_cart_item(db: Session, item_id: str) -> Optional[CartItem]:
    repo = CartItemRepository(db)
    return repo.get(item_id)
