from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from enum import Enum
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permission import require_roles
from app.schemas.response.base import BaseResponse
from app.schemas.response.product import ProductDetailResponse
from app.schemas.response.pagination import PaginatedResponse
from app.schemas.request.product import ProductCreateRequest, ProductUpdateRequest
from app.services.product_service import ProductService
from app.schemas.response.product import ProductVariantResponse, ProductVariantsListResponse
from app.models.product import Product
from app.models.productType import ProductType


router = APIRouter()


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class ProductSortBy(str, Enum):
    created_at = "created_at"
    name = "name"
    updated_at = "updated_at"


# ==================== GET ====================

@router.get("", response_model=BaseResponse[PaginatedResponse[ProductDetailResponse]])
def get_all_products(
    keyword: Optional[str] = Query(None, description="Tìm kiếm theo tên hoặc mô tả"),
    brand_id: Optional[str] = Query(None, description="Lọc theo thương hiệu"),
    category_id: Optional[str] = Query(None, description="Lọc theo danh mục"),
    min_price: Optional[float] = Query(None, ge=0, description="Giá tối thiểu"),
    max_price: Optional[float] = Query(None, ge=0, description="Giá tối đa"),
    is_active: Optional[bool] = Query(True, description="Lọc theo trạng thái hoạt động"),
    sort_by: ProductSortBy = Query(ProductSortBy.created_at, description="Sắp xếp theo"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Thứ tự sắp xếp"),
    skip: int = Query(0, ge=0, description="Số lượng bỏ qua"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng lấy"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách sản phẩm với tìm kiếm và lọc.
    
    - **keyword**: Tìm theo tên hoặc mô tả sản phẩm (không phân biệt hoa thường)
    - **brand_id**: Lọc theo ID thương hiệu
    - **category_id**: Lọc theo ID danh mục
    - **min_price**: Lọc sản phẩm có giá >= giá trị này
    - **max_price**: Lọc sản phẩm có giá <= giá trị này
    - **is_active**: Lọc theo trạng thái (mặc định: True - chỉ lấy sản phẩm đang hoạt động)
    - **sort_by**: Sắp xếp theo trường (created_at, name, updated_at)
    - **sort_order**: Thứ tự sắp xếp (asc, desc)
    """
    service = ProductService(db)
    products, total = service.search_with_filters(
        keyword=keyword,
        brand_id=brand_id,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        is_active=is_active,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
        skip=skip,
        limit=limit
    )
    
    paginated_data = PaginatedResponse(
        items=products,
        total=total,
        skip=skip,
        limit=limit
    )
    
    return BaseResponse(
        success=True, 
        message="Lấy danh sách sản phẩm thành công.", 
        data=paginated_data
    )


@router.get("/best-selling", response_model=BaseResponse[List[ProductDetailResponse]])
def get_best_selling_products(limit: int = 10, db: Session = Depends(get_db)):
    service = ProductService(db)
    result = service.get_best_selling(limit)
    products = [prod for prod, _ in result]
    return BaseResponse(success=True, message="Lấy top sản phẩm bán chạy thành công.", data=products)


@router.get("/most-favorite", response_model=BaseResponse[List[ProductDetailResponse]])
def get_most_favorite_products(limit: int = 10, db: Session = Depends(get_db)):
    service = ProductService(db)
    result = service.get_most_favorite(limit)
    products = [prod for prod, _ in result]
    return BaseResponse(success=True, message="Lấy top sản phẩm được yêu thích thành công.", data=products)


@router.get("/brand/{brand_id}", response_model=BaseResponse[List[ProductDetailResponse]])
def get_products_by_brand(
    brand_id: str,
    limit: int = Query(20, ge=1, le=100),
    skip: int = 0,
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    products = service.get_by_brand(brand_id, limit=limit, skip=skip)
    return BaseResponse(success=True, message="Lấy sản phẩm theo brand thành công.", data=products)


@router.get("/category/{category_id}", response_model=BaseResponse[List[ProductDetailResponse]])
def get_products_by_category(
    category_id: str,
    limit: int = Query(20, ge=1, le=100),
    skip: int = 0,
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    products = service.get_by_category(category_id, limit=limit, skip=skip)
    return BaseResponse(success=True, message="Lấy sản phẩm theo category thành công.", data=products)


@router.get("/{product_id}", response_model=BaseResponse[ProductDetailResponse])
def get_product_detail(product_id: str, db: Session = Depends(get_db)):
    service = ProductService(db)
    product = service.get_detail(product_id)
    if not product:
        return BaseResponse(success=False, message="Không tìm thấy sản phẩm.", data=None)
    return BaseResponse(success=True, message="Lấy thông tin sản phẩm thành công.", data=product)


# ==================== POST ====================

@router.post("", response_model=BaseResponse[ProductDetailResponse], status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """
    Tạo sản phẩm mới.
    - Chỉ admin mới có quyền
    """
    service = ProductService(db)
    product = service.create(data, created_by=current_user.id)
    
    # Refresh để lấy thông tin đầy đủ
    created_product = service.get_detail(product.id)
    return BaseResponse(
        success=True, 
        message="Tạo sản phẩm thành công.", 
        data=created_product
    )


# ==================== PUT ====================

@router.put("/{product_id}", response_model=BaseResponse[ProductDetailResponse])
def update_product(
    product_id: str,
    data: ProductUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """
    Cập nhật thông tin sản phẩm.
    - Chỉ admin mới có quyền
    """
    service = ProductService(db)
    
    # Kiểm tra sản phẩm tồn tại
    existing = service.get_detail(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sản phẩm."
        )
    
    updated = service.update(product_id, data, updated_by=current_user.id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cập nhật sản phẩm thất bại."
        )
    
    # Refresh để lấy thông tin đầy đủ
    updated_product = service.get_detail(product_id)
    return BaseResponse(
        success=True, 
        message="Cập nhật sản phẩm thành công.", 
        data=updated_product
    )

# ==================== DELETE ====================

@router.delete("/{product_id}", response_model=BaseResponse)
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """
    Xóa sản phẩm (soft delete).
    - Chỉ admin mới có quyền
    """
    service = ProductService(db)
    
    # Kiểm tra sản phẩm tồn tại
    existing = service.get_detail(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sản phẩm."
        )
    
    success = service.delete(product_id, deleted_by=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Xóa sản phẩm thất bại."
        )
    
    return BaseResponse(success=True, message="Xóa sản phẩm thành công.", data=None)
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
