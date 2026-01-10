from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.services.product_type_service import ProductTypeService
from app.schemas.response.product_type_schema import ProductTypeDetailResponse
from app.schemas.response.base import BaseResponse

router = APIRouter()


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
