from typing import Optional, Dict
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.database import SessionLocal


def get_db():
    """Yield a database session and ensure it's closed after use."""
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
    """Common pagination / filter / sort params used by routers.

    Returns a dict so routers/services can destructure as needed.
    """
    return {
        "skip": skip,
        "limit": limit,
        "q": q,
        "min_discount": min_discount,
        "max_discount": max_discount,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
    }
