from sqlalchemy.orm import Session, joinedload
from app.models.productType import ProductType
from typing import Optional


class ProductTypeRepository:

    def __init__(self, db: Session):
        self.db = db

    def get(self, product_type_id: str) -> Optional[ProductType]:
        """Get product type by ID"""
        return (
            self.db.query(ProductType)
            .filter(
                ProductType.id == product_type_id,
                ProductType.deleted_at.is_(None)
            )
            .first()
        )

    @staticmethod
    def get_by_product_and_variant_id(
        db: Session,
        product_id: str,
        variant_id: str
    ) -> ProductType | None:
        return (
            db.query(ProductType)
            .options(
                joinedload(ProductType.type_value)
            )
            .filter(
                ProductType.id == variant_id,
                ProductType.product_id == product_id,
                ProductType.deleted_at.is_(None)
            )
            .first()
        )

