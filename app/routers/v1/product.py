from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.services.product_service import ProductService
from app.schemas.response.product import ProductDetailResponse
from typing import List
router = APIRouter()

@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product_detail(product_id: str, db: Session = Depends(get_db)):
    service = ProductService(db)
    product = service.get_detail(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
@router.get("/best-selling", response_model=List[ProductDetailResponse])
def get_best_selling_products(limit: int = 10, db: Session = Depends(get_db)):
    service = ProductService(db)
    result = service.get_best_selling(limit)
    # lấy product từ tuple (Product, total_sold)
    return [prod for prod, _ in result]

@router.get("/most-favorite", response_model=List[ProductDetailResponse])
def get_most_favorite_products(limit: int = 10, db: Session = Depends(get_db)):
    service = ProductService(db)
    result = service.get_most_favorite(limit)
    # lấy product từ tuple (Product, avg_rating)
    return [prod for prod, _ in result]