from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from app.models.wishlist import Wishlist
from app.models.wishlistItem import WishlistItem
from app.models.productType import ProductType
from app.models.product import Product
from app.repositories.base import BaseRepository


class WishlistRepository(BaseRepository[Wishlist]):
    def __init__(self, db: Session):
        super().__init__(Wishlist, db)

    def get_by_user(self, user_id: str) -> Optional[Wishlist]:
        wishlist = self.db.query(Wishlist).filter(
            Wishlist.user_id == user_id,
            Wishlist.deleted_at.is_(None),
        ).options(
            joinedload(Wishlist.items)
                .joinedload(WishlistItem.product_type)
                .joinedload(ProductType.product)
        ).first()
        if wishlist and hasattr(wishlist, "items"):
            wishlist.items = [item for item in wishlist.items if item.deleted_at is None]
        return wishlist


class WishlistItemRepository(BaseRepository[WishlistItem]):
    def __init__(self, db: Session):
        super().__init__(WishlistItem, db)

    def get_by_wishlist_and_product(
        self, 
        wishlist_id: str, 
        product_type_id: str
    ) -> Optional[WishlistItem]:
        """Check if product already exists in wishlist"""
        return self.db.query(WishlistItem).filter(
            WishlistItem.wishlist_id == wishlist_id,
            WishlistItem.product_type_id == product_type_id,
            WishlistItem.deleted_at.is_(None)
        ).first()

    def list_by_wishlist(self, wishlist_id: str, skip: int = 0, limit: int = 100) -> Tuple[List[WishlistItem], int]:
        query = self.db.query(WishlistItem).filter(
            WishlistItem.wishlist_id == wishlist_id,
            WishlistItem.deleted_at.is_(None),
        ).options(
            joinedload(WishlistItem.product_type).joinedload(ProductType.product)
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

