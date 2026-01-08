
from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from enum import Enum

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permission import require_roles
from app.schemas.response.base import BaseResponse
from app.schemas.response.product import (
    ProductVariantResponse, 
    ProductVariantsListResponse,
    ProductCardResponse,
    ProductListResponse
)
from app.schemas.response.product import ProductDetailResponse
from app.schemas.response.pagination import PaginatedResponse
from app.schemas.request.product import ProductCreateRequest, ProductUpdateRequest
from app.services.product_service import ProductService
from app.schemas.response.product import ProductVariantResponse, ProductVariantsListResponse

from app.models.product import Product
from app.models.productType import ProductType
from app.models.review import Review
from app.repositories.product_repository import ProductRepository


router = APIRouter()


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class ProductSortBy(str, Enum):
    created_at = "created_at"
    name = "name"
    updated_at = "updated_at"


# ==================== GET (Public) ====================

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
    """Lấy danh sách sản phẩm với tìm kiếm và lọc (Public)"""
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


@router.get("/category/{category_id}", response_model=BaseResponse[PaginatedResponse[ProductDetailResponse]])
def get_products_by_category(
    category_id: str,
    limit: int = Query(20, ge=1, le=100),
    skip: int = 0,
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    products, total = service.search_with_filters(
        category_id=category_id,
        is_active=True,
        skip=skip,
        limit=limit
    )
    paginated_data = PaginatedResponse(
        items=products,
        total=total,
        skip=skip,
        limit=limit
    )
    return BaseResponse(success=True, message="Lấy sản phẩm theo category thành công.", data=paginated_data)


@router.get("/{product_id}", response_model=BaseResponse[ProductDetailResponse])
def get_product_detail(product_id: str, db: Session = Depends(get_db)):
    service = ProductService(db)
    product = service.get_detail(product_id)
    if not product:
        return BaseResponse(success=False, message="Không tìm thấy sản phẩm.", data=None)
    return BaseResponse(success=True, message="Lấy thông tin sản phẩm thành công.", data=product)


# ==================== POST/PUT/DELETE (Admin only) ====================

@router.post("", response_model=BaseResponse[ProductDetailResponse], status_code=status.HTTP_201_CREATED)
async def create_product(
    name: str = Form(..., description="Tên sản phẩm"),
    brand_id: Optional[str] = Form(None, description="ID thương hiệu"),
    category_id: Optional[str] = Form(None, description="ID danh mục"),
    description: Optional[str] = Form(None, description="Mô tả sản phẩm"),
    is_active: bool = Form(True, description="Trạng thái hoạt động"),
    thumbnail: Optional[UploadFile] = File(None, description="File ảnh thumbnail"),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """
    Tạo sản phẩm mới với upload thumbnail (Admin only)
    
    - **name**: Tên sản phẩm (bắt buộc)
    - **brand_id**: ID thương hiệu
    - **category_id**: ID danh mục
    - **description**: Mô tả sản phẩm
    - **is_active**: Trạng thái (mặc định: true)
    - **thumbnail**: File ảnh thumbnail (jpg, png, gif, webp)
    """
    from app.services.upload_product_service import save_upload_file, get_upload_url
    
    # Xử lý upload thumbnail nếu có
    thumbnail_path = None
    if thumbnail and thumbnail.filename:
        saved_filename = await save_upload_file(thumbnail, "products")
        thumbnail_path = get_upload_url(saved_filename)
    
    # Tạo request data
    product_data = ProductCreateRequest(
        name=name,
        brand_id=brand_id,
        category_id=category_id,
        description=description,
        thumbnail=thumbnail_path,
        is_active=is_active
    )
    
    service = ProductService(db)
    product = service.create(product_data, created_by=current_user.id)
    created_product = service.get_detail(product.id)
    
    return BaseResponse(
        success=True, 
        message="Tạo sản phẩm thành công.", 
        data=created_product
    )


@router.put("/{product_id}", response_model=BaseResponse[ProductDetailResponse])
def update_product(
    product_id: str,
    data: ProductUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """Cập nhật thông tin sản phẩm (Admin only)"""
    service = ProductService(db)
    
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
    
    updated_product = service.get_detail(product_id)
    return BaseResponse(
        success=True, 
        message="Cập nhật sản phẩm thành công.", 
        data=updated_product
    )


@router.delete("/{product_id}", response_model=BaseResponse)
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """Xóa sản phẩm (Admin only, soft delete)"""
    service = ProductService(db)
    
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


# ==================== Upload Thumbnail ====================

@router.post("/{product_id}/thumbnail", response_model=BaseResponse[ProductDetailResponse])
async def upload_product_thumbnail(
    product_id: str,
    file: UploadFile = File(..., description="File ảnh thumbnail"),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """
    Upload thumbnail cho sản phẩm (Admin only)
    
    - **file**: File ảnh (jpg, jpeg, png, gif, webp)
    
    Ảnh sẽ được lưu với tên unique: {timestamp}_{uuid}_{original_name}
    """
    from app.services.upload_product_service import save_upload_file, get_upload_url
    
    service = ProductService(db)
    
    # Kiểm tra sản phẩm tồn tại
    existing = service.get_detail(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sản phẩm."
        )
    
    # Upload file
    saved_filename = await save_upload_file(file, "products")
    thumbnail_url = get_upload_url(saved_filename)
    
    # Cập nhật sản phẩm với thumbnail mới
    from app.schemas.request.product import ProductUpdateRequest
    update_data = ProductUpdateRequest(thumbnail=thumbnail_url)
    service.update(product_id, update_data, updated_by=current_user.id)
    
    # Lấy lại thông tin sản phẩm đã cập nhật
    updated_product = service.get_detail(product_id)
    
    return BaseResponse(
        success=True,
        message="Upload thumbnail thành công.",
        data=updated_product
    )

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
