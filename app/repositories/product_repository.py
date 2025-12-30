from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.dependencies.database import get_db
from app.schemas.response.base import BaseResponse
from app.schemas.response.product import ProductDetailResponse, ProductTypeResponse
from app.services.product_service import ProductService

router = APIRouter()

@router.get("/{product_id}", response_model=BaseResponse[ProductDetailResponse])
def get_product_detail(product_id: str, db: Session = Depends(get_db)):
    service = ProductService(db)
    product = service.get_detail(product_id)
    if not product:
        return BaseResponse(success=False, message="Không tìm thấy sản phẩm.", data=None)
    return BaseResponse(success=True, data=product)

@router.get("/brand/{brand_id}", response_model=BaseResponse[List[ProductDetailResponse]])
def get_products_by_brand(
    brand_id: str,
    limit: int = Query(20, ge=1, le=100),
    skip: int = 0,
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    products = service.get_by_brand(brand_id, limit=limit, skip=skip)
    return BaseResponse(success=True, data=products)

@router.get("/category/{category_id}", response_model=BaseResponse[List[ProductDetailResponse]])
def get_products_by_category(
    category_id: str,
    limit: int = Query(20, ge=1, le=100),
    skip: int = 0,
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    products = service.get_by_category(category_id, limit=limit, skip=skip)
    return BaseResponse(success=True, data=products)

@router.get("/best-selling", response_model=BaseResponse[List[ProductDetailResponse]])
def get_best_selling_products(limit: int = 10, db: Session = Depends(get_db)):
    service = ProductService(db)
    result = service.get_best_selling(limit)
    products = [prod for prod, _ in result]
    return BaseResponse(success=True, data=products)

@router.get("/most-favorite", response_model=BaseResponse[List[ProductDetailResponse]])
def get_most_favorite_products(limit: int = 10, db: Session = Depends(get_db)):
    service = ProductService(db)
    result = service.get_most_favorite(limit)
    products = [prod for prod, _ in result]
    return BaseResponse(success=True, data=products)