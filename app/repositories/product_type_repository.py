from sqlalchemy.orm import Session, joinedload
from app.models.productType import ProductType
from typing import Optional


class ProductTypeRepository:
    @staticmethod
    def get_top_discounted_with_sold(db: Session, limit: int = 6):
        """
        Lấy các product_types có phần trăm giảm giá lớn nhất, kèm số lượng đã bán thực tế
        """
        from app.models.orderDetail import OrderDetail
        from sqlalchemy import func, desc
        # Tính phần trăm giảm giá và tổng số đã bán
        query = (
            db.query(
                ProductType,
                ((ProductType.price - ProductType.discount_price) / ProductType.price * 100).label("discount_percent"),
                func.coalesce(func.sum(OrderDetail.number), 0).label("sold")
            )
            .outerjoin(OrderDetail, OrderDetail.product_type_id == ProductType.id)
            .filter(ProductType.discount_price < ProductType.price, ProductType.deleted_at.is_(None))
            .group_by(ProductType.id)
            .order_by(desc("discount_percent"))
            .limit(limit)
        )
        return query.all()

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

