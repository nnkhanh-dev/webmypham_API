from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.address import Address
from app.repositories.base import BaseRepository


class AddressRepository(BaseRepository[Address]):
    """Repository cho Address model"""
    
    def __init__(self, db: Session):
        super().__init__(Address, db)
    
    def get_by_user(self, user_id: str, address_id: str) -> Optional[Address]:
        """Lấy một địa chỉ của user theo ID"""
        return self.db.query(Address).filter(
            and_(
                Address.id == address_id,
                Address.user_id == user_id,
                Address.deleted_at.is_(None)
            )
        ).first()
    
    def list_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> Tuple[List[Address], int]:
        """Lấy danh sách địa chỉ của user"""
        query = self.db.query(Address).filter(
            and_(
                Address.user_id == user_id,
                Address.deleted_at.is_(None)
            )
        ).order_by(Address.is_default.desc(), Address.created_at.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
    
    def get_default_address(self, user_id: str) -> Optional[Address]:
        """Lấy địa chỉ mặc định của user"""
        return self.db.query(Address).filter(
            and_(
                Address.user_id == user_id,
                Address.is_default == True,
                Address.deleted_at.is_(None)
            )
        ).first()
    
    def unset_all_defaults(self, user_id: str) -> None:
        """Bỏ đặt tất cả địa chỉ của user làm mặc định"""
        self.db.query(Address).filter(
            and_(
                Address.user_id == user_id,
                Address.is_default == True,
                Address.deleted_at.is_(None)
            )
        ).update({"is_default": False})
        self.db.commit()

