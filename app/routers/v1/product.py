from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.dependencies.database import get_db
from app.schemas.response.base import BaseResponse
from app.schemas.response.product import (
    ProductVariantResponse, 
    ProductVariantsListResponse,
    ProductCardResponse,
    ProductListResponse
)
from app.models.product import Product
from app.models.productType import ProductType
from app.models.review import Review
from app.repositories.product_repository import ProductRepository


router = APIRouter()


def transform_product_to_card(product: Product, db: Session, avg_rating: float = None, review_count: int = None, total_sold: int = None) -> ProductCardResponse:
    """Helper function để transform Product thành ProductCardResponse"""
    # Lấy giá từ product_types
    prices = [pt.price for pt in product.product_types if pt.price and pt.deleted_at is None]
    discount_prices = [pt.discount_price for pt in product.product_types if pt.discount_price and pt.deleted_at is None]
    
    # Nếu chưa có review_count, tính từ DB
    if review_count is None:
        review_count = db.query(func.count(Review.id)).filter(
            Review.product_id == product.id,
            Review.deleted_at.is_(None)
        ).scalar() or 0
    
    # Nếu chưa có avg_rating, tính từ DB
    if avg_rating is None and review_count > 0:
        avg_rating = db.query(func.avg(Review.rating)).filter(
            Review.product_id == product.id,
            Review.deleted_at.is_(None)
        ).scalar()
    
    return ProductCardResponse(
        id=product.id,
        name=product.name,
        thumbnail=product.thumbnail,
        description=product.description,
        brand_name=product.brand.name if product.brand else None,
        category_name=product.category.name if product.category else None,
        min_price=min(prices) if prices else None,
        max_price=max(prices) if prices else None,
        min_discount_price=min(discount_prices) if discount_prices else None,
        avg_rating=round(avg_rating, 1) if avg_rating else None,
        review_count=review_count,
        total_sold=total_sold or 0
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


# --- Homepage APIs ---

@router.get("/homepage/best-selling", response_model=BaseResponse[ProductListResponse])
def get_best_selling_products(
    limit: int = Query(default=8, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Lấy danh sách sản phẩm bán chạy nhất cho homepage"""
    repo = ProductRepository(db)
    results = repo.get_best_selling(limit)
    
    items = []
    for product, total_sold in results:
        card = transform_product_to_card(product, db, total_sold=int(total_sold) if total_sold else 0)
        items.append(card)
    
    return BaseResponse(
        success=True, 
        message="Lấy sản phẩm bán chạy thành công.",
        data=ProductListResponse(items=items, total=len(items))
    )


@router.get("/homepage/top-rated", response_model=BaseResponse[ProductListResponse])
def get_top_rated_products(
    limit: int = Query(default=8, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Lấy danh sách sản phẩm rating cao nhất cho homepage"""
    repo = ProductRepository(db)
    results = repo.get_top_rated(limit)
    
    items = []
    for product, avg_rating, review_count in results:
        card = transform_product_to_card(
            product, db, 
            avg_rating=float(avg_rating) if avg_rating else None,
            review_count=int(review_count)
        )
        items.append(card)
    
    return BaseResponse(
        success=True, 
        message="Lấy sản phẩm rating cao thành công.",
        data=ProductListResponse(items=items, total=len(items))
    )


@router.get("/homepage/new-arrivals", response_model=BaseResponse[ProductListResponse])
def get_new_arrivals(
    limit: int = Query(default=8, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Lấy danh sách sản phẩm mới nhất cho homepage"""
    repo = ProductRepository(db)
    products = repo.get_new_arrivals(limit)
    
    items = [transform_product_to_card(p, db) for p in products]
    
    return BaseResponse(
        success=True, 
        message="Lấy sản phẩm mới thành công.",
        data=ProductListResponse(items=items, total=len(items))
    )


@router.get("/homepage/most-favorite", response_model=BaseResponse[ProductListResponse])
def get_most_favorite_products(
    limit: int = Query(default=8, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Lấy danh sách sản phẩm được yêu thích nhất cho homepage"""
    repo = ProductRepository(db)
    results = repo.get_most_favorite(limit)
    
    items = []
    for product, favorite_count in results:
        card = transform_product_to_card(product, db)
        card.favorite_count = int(favorite_count)
        items.append(card)
    
    return BaseResponse(
        success=True, 
        message="Lấy sản phẩm yêu thích thành công.",
        data=ProductListResponse(items=items, total=len(items))
    )