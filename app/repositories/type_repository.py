from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, asc, desc
from app.models.type import Type
from app.repositories.base import BaseRepository


class TypeRepository(BaseRepository[Type]):
    def __init__(self, db: Session):
        super().__init__(Type, db)

    def get_by_name(self, name: str) -> Optional[Type]:
        return self.db.query(Type).filter(
            Type.name == name,
            Type.deleted_at.is_(None),
        ).first()

    def search(
        self,
        skip: int = 0,
        limit: int = 100,
        q: Optional[str] = None,
        sort_by: str = "id",
        sort_dir: str = "desc",
    ) -> Tuple[List[Type], int]:
        query = self.db.query(Type).options(
            joinedload(Type.values)  # Load type_values relationship
        ).filter(Type.deleted_at.is_(None))

        if q:
            like = f"%{q}%"
            query = query.filter(
                or_(
                    Type.name.ilike(like),
                    Type.description.ilike(like),
                )
            )

        total = query.count()

        sort_col = getattr(Type, sort_by, None)
        if sort_col is None:
            sort_col = Type.id

        if sort_dir and sort_dir.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        items = query.offset(skip).limit(limit).all()
        return items, total
