from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc
from app.models.voucher import Voucher
from app.schemas.voucher import VoucherCreate, VoucherUpdate


def get_voucher(db: Session, voucher_id: int) -> Optional[Voucher]:
    return db.query(Voucher).filter(Voucher.id == voucher_id, Voucher.deleted_at.is_(None)).first()


def get_voucher_by_code(db: Session, code: str) -> Optional[Voucher]:
    return db.query(Voucher).filter(Voucher.code == code, Voucher.deleted_at.is_(None)).first()


def get_vouchers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = None,
    min_discount: Optional[float] = None,
    max_discount: Optional[float] = None,
    sort_by: str = "id",
    sort_dir: str = "desc",
) -> Tuple[List[Voucher], int]:
    """Return (items, total) with optional search, filter and sorting."""
    query = db.query(Voucher).filter(Voucher.deleted_at.is_(None))

    if q:
        like = f"%{q}%"
        query = query.filter(or_(Voucher.code.ilike(like), Voucher.description.ilike(like)))

    if min_discount is not None:
        query = query.filter(Voucher.discount >= min_discount)
    if max_discount is not None:
        query = query.filter(Voucher.discount <= max_discount)

    total = query.count()

    # sorting
    sort_col = getattr(Voucher, sort_by, None)
    if sort_col is None:
        sort_col = Voucher.id
    if sort_dir and sort_dir.lower() == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    items = query.offset(skip).limit(limit).all()
    return items, total

def create_voucher(db: Session, voucher_in: VoucherCreate, created_by: Optional[int] = None) -> Voucher:
    obj = Voucher(**voucher_in.dict())
    if created_by is not None:
        obj.created_by = created_by
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_voucher(db: Session, voucher_id: int, voucher_in: VoucherUpdate, updated_by: Optional[int] = None) -> Optional[Voucher]:
    obj = db.query(Voucher).filter(Voucher.id == voucher_id, Voucher.deleted_at.is_(None)).first()
    if not obj:
        return None
    update_data = voucher_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)
    if updated_by is not None:
        obj.updated_by = updated_by
    # ensure updated_at changes on update
    obj.updated_at = datetime.utcnow() + timedelta(hours=7)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def soft_delete_voucher(db: Session, voucher_id: int, deleted_by: Optional[int] = None) -> bool:
    obj = db.query(Voucher).filter(Voucher.id == voucher_id, Voucher.deleted_at.is_(None)).first()
    if not obj:
        return False
    obj.deleted_at = datetime.utcnow() + timedelta(hours=7)
    if deleted_by is not None:
        obj.deleted_by = deleted_by
    db.add(obj)
    db.commit()
    return True