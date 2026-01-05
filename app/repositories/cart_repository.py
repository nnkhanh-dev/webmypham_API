from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from app.models.cart import Cart
from app.models.cartItem import CartItem
from app.models.productType import ProductType
from app.repositories.base import BaseRepository


class CartRepository(BaseRepository[Cart]):
    def __init__(self, db: Session):
        super().__init__(Cart, db)

    def get_by_user(self, user_id: str) -> Optional[Cart]:
        """Lấy giỏ hàng với đầy đủ thông tin sản phẩm"""
        return self.db.query(Cart).options(
            joinedload(Cart.items)
            .joinedload(CartItem.product_type)
            .joinedload(ProductType.product),  # Load thông tin sản phẩm
            joinedload(Cart.items)
            .joinedload(CartItem.product_type)
            .joinedload(ProductType.type_value),  # Load tên biến thể (màu, dung tích)
        ).filter(
            Cart.user_id == user_id,
            Cart.deleted_at.is_(None),
        ).first()


    def get_by_id_and_user(self, cart_id: str, user_id: str) -> Optional[Cart]:
        return self.db.query(Cart).filter(
            Cart.id == cart_id,
            Cart.user_id == user_id,
            Cart.deleted_at.is_(None),
        ).first()


class CartItemRepository(BaseRepository[CartItem]):
    def __init__(self, db: Session):
        super().__init__(CartItem, db)

    def list_by_cart(self, cart_id: str, skip: int = 0, limit: int = 100) -> Tuple[List[CartItem], int]:
        query = self.db.query(CartItem).filter(
            CartItem.cart_id == cart_id,
            CartItem.deleted_at.is_(None),
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_cart_and_product(self, cart_id: str, product_type_id: str) -> Optional[CartItem]:
        return self.db.query(CartItem).filter(
            CartItem.cart_id == cart_id,
            CartItem.product_type_id == product_type_id,
            CartItem.deleted_at.is_(None),
        ).first()
