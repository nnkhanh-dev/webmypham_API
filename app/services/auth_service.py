from typing import Optional

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.schemas.request.auth import UserCreate

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Lấy user theo email (sử dụng repository)"""
    user_repo = UserRepository(db)
    return user_repo.get_by_email(email)


def verify_password(plain: str, hashed: str) -> bool:
    """Xác thực password"""
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def create_user(db: Session, user_in: UserCreate, role_name: str = "CLIENT", created_by: Optional[str] = None) -> User:
    """Tạo user mới và gán role (mặc định CLIENT). Tạo role nếu chưa tồn tại."""
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    
    hashed = pwd_context.hash(user_in.password)
    
    user_data = {
        "email": user_in.email,
        "password_hash": hashed,
        "first_name": user_in.first_name,
        "last_name": user_in.last_name,
        "phone_number": user_in.phone_number,
    }
    
    user = user_repo.create(user_data, created_by=created_by)
    
    # Lấy hoặc tạo role
    role = role_repo.get_or_create(role_name, created_by=created_by)
    
    # Gán role cho user
    user = user_repo.assign_role(user, role.name)
    
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        print(f"DEBUG: Không tìm thấy email {email}")
        return None
    is_valid = verify_password(password, getattr(user, "password_hash", ""))
    if not is_valid:
        print(f"DEBUG: Mật khẩu không khớp cho email {email}")
        return None
    return user
