from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from app.models.wishlist import Wishlist
from app.models.wishlistItem import WishlistItem
from app.repositories.wishlist_repository import WishlistRepository, WishlistItemRepository
from app.schemas.request.wishlist import WishlistItemCreate


def get_wishlist_by_user(db: Session, user_id: str) -> Optional[Wishlist]:
    """Get wishlist for a specific user"""
    repo = WishlistRepository(db)
    return repo.get_by_user(user_id)


def create_wishlist_for_user(db: Session, user_id: str, created_by: Optional[str] = None) -> Wishlist:
    """
    Create wishlist for user (idempotent - returns existing if found)
    """
    repo = WishlistRepository(db)
    existing = repo.get_by_user(user_id)
    if existing:
        return existing
    data = {"user_id": user_id}
    return repo.create(data, created_by=created_by)


def add_wishlist_item(
    db: Session, 
    wishlist_id: str, 
    item_in: WishlistItemCreate, 
    created_by: Optional[str] = None
) -> WishlistItem:
    """
    Add item to wishlist. Raises ValueError if item already exists.
    """
    repo = WishlistItemRepository(db)
    
    # Check if item already exists
    existing = repo.get_by_wishlist_and_product(
        wishlist_id, 
        item_in.product_type_id
    )
    
    if existing:
        raise ValueError("Sản phẩm đã có trong danh sách yêu thích")
    
    # Create new item
    data = item_in.dict()
    data["wishlist_id"] = wishlist_id
    return repo.create(data, created_by=created_by)


def list_wishlist_items(db: Session, wishlist_id: str, skip: int = 0, limit: int = 100) -> Tuple[List[WishlistItem], int]:
    """Get paginated list of items in wishlist"""
    repo = WishlistItemRepository(db)
    return repo.list_by_wishlist(wishlist_id, skip=skip, limit=limit)


def remove_wishlist_item(db: Session, item_id: str, deleted_by: Optional[str] = None) -> bool:
    """Soft delete wishlist item"""
    repo = WishlistItemRepository(db)
    return repo.delete(item_id, deleted_by=deleted_by)


def get_wishlist_item(db: Session, item_id: str) -> Optional[WishlistItem]:
    """Get single wishlist item by ID"""
    repo = WishlistItemRepository(db)
    return repo.get(item_id)

