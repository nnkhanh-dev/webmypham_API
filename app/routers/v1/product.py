from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.dependencies.database import get_db
from app.schemas.response.base import BaseResponse
from app.schemas.response.product import ProductVariantResponse, ProductVariantsListResponse
from app.models.product import Product
from app.models.productType import ProductType


router = APIRouter()


@router.get("/{product_id}/variants", response_model=BaseResponse[ProductVariantsListResponse])
def get_product_variants(product_id: str, db: Session = Depends(get_db)):
    """
    Lấy danh sách tất cả biến thể của sản phẩm.
    Dùng khi user click "Đổi phân loại" trong giỏ hàng.
    """
    # Lấy product
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.deleted_at.is_(None)
    ).first()
    
    if not product:
        return BaseResponse(success=False, message="Không tìm thấy sản phẩm.", data=None)
    
    # Lấy tất cả variants với eager loading type_value
    variants = db.query(ProductType).options(
        joinedload(ProductType.type_value)
    ).filter(
        ProductType.product_id == product_id,
        ProductType.deleted_at.is_(None)
    ).all()
    
    # Transform variants with is_available computed
    variant_list = []
    for v in variants:
        variant_data = ProductVariantResponse(
            id=v.id,
            price=v.price,
            discount_price=v.discount_price,
            stock=v.stock,
            image_path=v.image_path,
            volume=v.volume,
            skin_type=v.skin_type,
            origin=v.origin,
            status=v.status,
            type_value=v.type_value,
            is_available=(v.stock is None or v.stock > 0)  # False nếu stock = 0
        )
        variant_list.append(variant_data)
    
    result = ProductVariantsListResponse(
        product_id=product.id,
        product_name=product.name,
        product_thumbnail=product.thumbnail,
        variants=variant_list
    )
    
    return BaseResponse(success=True, message="Lấy danh sách biến thể thành công.", data=result)