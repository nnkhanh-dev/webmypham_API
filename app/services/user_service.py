from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.request.auth import UserUpdate
from app.core.exceptions.user_exception import UserNotFoundException

def get_user(db: Session, user_id: str) -> Optional[User]:
    repo = UserRepository(db)
    if not user_id:
        raise UserNotFoundException(user_id)
    return repo.get_with_roles(user_id)


def list_users(db: Session, skip: int = 0, limit: int = 100, q: Optional[str] = None) -> Tuple[List[User], int]:
    # simple search by name or email
    query = db.query(User).filter(User.deleted_at.is_(None))
    if q:
        like = f"%{q}%"
        query = query.filter((User.name.ilike(like)) | (User.email.ilike(like)))
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def update_user(db: Session, user_id: str, user_in: UserUpdate, updated_by: Optional[str] = None) -> Optional[User]:
    repo = UserRepository(db)
    if not user_id:
        raise UserNotFoundException(user_id)
    data = user_in.dict(exclude_unset=True)
    return repo.update(user_id, data, updated_by=updated_by)


def delete_user(db: Session, user_id: str, deleted_by: Optional[str] = None) -> bool:
    repo = UserRepository(db)
    if not user_id:
        raise UserNotFoundException(user_id)
    return repo.delete(user_id, deleted_by=deleted_by)
