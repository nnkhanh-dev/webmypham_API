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
    
    # Get existing cart item
    item = repo.get(item_id)
    if not item:
        return None
    
    # If updating product_type_id (changing variant), validate new product type
    if "product_type_id" in data and data["product_type_id"] != item.product_type_id:
        new_product_type = db.query(ProductType).filter(
            ProductType.id == data["product_type_id"], 
            ProductType.deleted_at.is_(None)
        ).first()
        if not new_product_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New product type not found")
        
        # Check if changing to an item that already exists in cart (merge or reject)
        existing_same_type = repo.get_by_cart_and_product(item.cart_id, data["product_type_id"])
        if existing_same_type and existing_same_type.id != item_id:
            # Calculate combined quantity
            new_qty = int(data.get("quantity", item.quantity))
            combined_qty = existing_same_type.quantity + new_qty
            
            # Validate combined quantity against stock
            if new_product_type.stock is not None and combined_qty > new_product_type.stock:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Không đủ tồn kho: yêu cầu {combined_qty}, còn {new_product_type.stock}"
                )
            
            # Update existing item with combined quantity
            repo.update(existing_same_type.id, {"quantity": combined_qty}, updated_by=updated_by)
            
            # Delete original item (it's been merged)
            repo.delete(item_id, deleted_by=updated_by)
            
            # Return the merged item
            return repo.get(existing_same_type.id)
        
        # Validate stock for new product type
        new_qty = int(data.get("quantity", item.quantity))
        if new_product_type.stock is not None and new_qty > new_product_type.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Insufficient stock for new variant: requested {new_qty}, available {new_product_type.stock}"
            )
    
    # If only updating quantity (no product_type_id change), validate against current product type stock
    elif "quantity" in data:
        product_type = db.query(ProductType).filter(
            ProductType.id == item.product_type_id, 
            ProductType.deleted_at.is_(None)
        ).first()
        if not product_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product type not found")
        new_qty = int(data["quantity"])
        if product_type.stock is not None and new_qty > product_type.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Insufficient stock: requested {new_qty}, available {product_type.stock}"
            )

    return repo.update(item_id, data, updated_by=updated_by)


def delete_cart_item(db: Session, item_id: str, deleted_by: Optional[str] = None) -> bool:
    repo = CartItemRepository(db)
    return repo.delete(item_id, deleted_by=deleted_by)


def get_cart_item(db: Session, item_id: str) -> Optional[CartItem]:
    repo = CartItemRepository(db)
    return repo.get(item_id)
