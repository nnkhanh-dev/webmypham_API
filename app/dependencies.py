from typing import Optional, Dict
from sqlalchemy.orm import Session
from fastapi import Depends, Request, HTTPException, status
from app.db.database import SessionLocal

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_pagination(
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = None,
    min_discount: Optional[float] = None,
    max_discount: Optional[float] = None,
    sort_by: str = "id",
    sort_dir: str = "desc",
) -> Dict:
    return {"skip": skip, "limit": limit, "q": q, "min_discount": min_discount, "max_discount": max_discount, "sort_by": sort_by, "sort_dir": sort_dir}

def require_roles(*roles: str):
    def checker(request: Request):
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        user_role_names = [r.name for r in getattr(user, "roles", [])]
        if not any(r in user_role_names for r in roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user
    return checker

def get_current_user(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user