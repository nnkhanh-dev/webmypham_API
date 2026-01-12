from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.user import User
from app.models.role import Role
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository cho User model"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Lấy user theo email (không bao gồm deleted)"""
        return self.db.query(User).filter(
            and_(
                User.email == email,
                User.deleted_at.is_(None)
            )
        ).first()
    
    def get_by_phone(self, phone_number: str) -> Optional[User]:
        """Lấy user theo số điện thoại (không bao gồm deleted)"""
        return self.db.query(User).filter(
            and_(
                User.phone_number == phone_number,
                User.deleted_at.is_(None)
            )
        ).first()
    
    def get_with_roles(self, user_id: str) -> Optional[User]:
        """Lấy user kèm roles"""
        return self.db.query(User).filter(
            and_(
                User.id == user_id,
                User.deleted_at.is_(None)
            )
        ).first()
    
    def assign_role(self, user: User, role_name: str) -> User:
        """Gán role cho user (tạo role nếu chưa tồn tại)"""
        role = self.db.query(Role).filter(Role.name.ilike(role_name)).first()
        if not role:
            role = Role(name=role_name.upper())
            self.db.add(role)
            self.db.flush()
        
        if role not in user.roles:
            user.roles.append(role)
            self.db.commit()
            self.db.refresh(user)
        
        return user
    
    def remove_role(self, user: User, role_name: str) -> User:
        """Gỡ role khỏi user"""
        role = self.db.query(Role).filter(Role.name.ilike(role_name)).first()
        if role and role in user.roles:
            user.roles.remove(role)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def get_by_reset_token(self, token: str) -> Optional[User]:
        """Lấy user theo reset password token (không bao gồm deleted)"""
        return self.db.query(User).filter(
            and_(
                User.reset_password_token == token,
                User.deleted_at.is_(None)
            )
        ).first()

