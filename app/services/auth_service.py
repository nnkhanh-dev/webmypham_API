from typing import Optional

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role
from app.schemas.auth import UserCreate

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def create_user(db: Session, user_in: UserCreate, role_name: str = "CLIENT") -> User:
    """Create a user and assign a role (default CLIENT). Creates the role if missing."""
    # use Argon2 via passlib for hashing (supports long passwords)
    hashed = pwd_context.hash(user_in.password)
    user = User(
        email=user_in.email,
        password_hash=hashed,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        phone_number=user_in.phone_number,
    )
    db.add(user)
    db.flush()

    # find or create role
    role = db.query(Role).filter(Role.name.ilike(role_name)).first()
    if not role:
        role = Role(name=role_name.upper())
        db.add(role)
        db.flush()

    # associate role with user
    user.roles.append(role)

    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, getattr(user, "password_hash", "")):
        return None
    return user
