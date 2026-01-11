from sqlalchemy.orm import Session
from app.repositories.product_type_repository import ProductTypeRepository
from app.core.exceptions.app_exception import NotFoundException


class ProductTypeService:

    @staticmethod
    def get_top_discounted_with_sold(db: Session, limit: int = 6):
        result = ProductTypeRepository.get_top_discounted_with_sold(db, limit)
        # Trả về danh sách dict gồm: product_type, discount_percent, sold
        return [
            {
                "product_type": pt,
                "discount_percent": round(discount_percent, 2) if discount_percent is not None else 0,
                "sold": sold
            }
            for pt, discount_percent, sold in result
        ]

    @staticmethod
    def get_variant_detail(
        db: Session,
        product_id: str,
        variant_id: str
    ):
        variant = ProductTypeRepository.get_by_product_and_variant_id(
            db=db,
            product_id=product_id,
            variant_id=variant_id
        )

        if not variant:
            raise NotFoundException(
                message="Không tìm thấy biến thể sản phẩm"
            )

        return variant
