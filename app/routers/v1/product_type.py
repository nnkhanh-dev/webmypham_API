from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.services.product_type_service import ProductTypeService
from app.schemas.response.product_type_schema import ProductTypeDetailResponse
from app.schemas.response.base import BaseResponse

router = APIRouter()


# API lấy 6 sản phẩm giảm giá lớn nhất
from app.schemas.response.product import ProductTypeResponse
from typing import List

@router.get("/top-discounted", response_model=BaseResponse[List[dict]])
def get_top_discounted_product_types(db: Session = Depends(get_db), limit: int = 6):
    """
    Lấy 6 product_types có phần trăm giảm giá lớn nhất, trả về phần trăm giảm giá và số lượng đã bán
    """
    result = ProductTypeService.get_top_discounted_with_sold(db, limit)
    # Trả về dạng: [{product_type: ..., discount_percent: ..., sold: ...}]
    return BaseResponse(
        success=True,
        message="Lấy top sản phẩm giảm giá lớn nhất thành công",
        data=result
    )


@router.get(
    "/{product_id}/types/{variant_id}",
    response_model=BaseResponse[ProductTypeDetailResponse]
)
def get_product_variant_detail(
    product_id: str,
    variant_id: str,
    db: Session = Depends(get_db)
):
    """
    Lấy chi tiết 1 biến thể sản phẩm
    - Dùng khi click vào biến thể (edit)
    """
    variant = ProductTypeService.get_variant_detail(
        db=db,
        product_id=product_id,
        variant_id=variant_id
    )

    return BaseResponse(
        success=True,
        message="Lấy chi tiết biến thể sản phẩm thành công",
        data=ProductTypeDetailResponse.from_orm(variant)
    )
