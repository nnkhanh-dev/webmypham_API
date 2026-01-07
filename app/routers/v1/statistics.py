"""
Statistics Router - API thống kê cho Admin
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel
from datetime import datetime

from app.dependencies.database import get_db
from app.dependencies.permission import require_roles
from app.schemas.response.base import BaseResponse
from app.models.product import Product
from app.models.productType import ProductType
from app.models.order import Order
from app.models.orderDetail import OrderDetail

router = APIRouter()


class TopFilter(int, Enum):
    top_5 = 5
    top_10 = 10
    top_15 = 15
    top_20 = 20


class BestSellingProductResponse(BaseModel):
    """Response cho sản phẩm bán chạy"""
    id: str
    name: str
    thumbnail: Optional[str] = None
    category_id: Optional[str] = None
    brand_id: Optional[str] = None
    total_sold: int
    total_revenue: float

    class Config:
        from_attributes = True


class ProductStatisticsResponse(BaseModel):
    """Response cho thống kê sản phẩm"""
    total_products: int
    total_active_products: int
    total_sold_items: int
    total_revenue: float
    best_selling: List[BestSellingProductResponse]


@router.get("/products/best-selling", response_model=BaseResponse[List[BestSellingProductResponse]])
def get_best_selling_statistics(
    top: TopFilter = Query(TopFilter.top_10, description="Số lượng top sản phẩm: 5, 10, 15, 20"),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """
    Thống kê sản phẩm bán chạy nhất (Admin only)
    
    - **top**: Số lượng top sản phẩm (5, 10, 15, 20)
    
    Returns danh sách sản phẩm với:
    - total_sold: Tổng số lượng đã bán
    - total_revenue: Tổng doanh thu
    """
    # Query sản phẩm bán chạy với doanh thu
    results = db.query(
        Product.id,
        Product.name,
        Product.thumbnail,
        Product.category_id,
        Product.brand_id,
        func.coalesce(func.sum(ProductType.sold), 0).label('total_sold'),
        func.coalesce(
            func.sum(ProductType.sold * func.coalesce(ProductType.discount_price, ProductType.price)),
            0
        ).label('total_revenue')
    ).outerjoin(
        ProductType, Product.id == ProductType.product_id
    ).filter(
        Product.deleted_at.is_(None),
        Product.is_active == True
    ).group_by(
        Product.id
    ).order_by(
        desc('total_sold')
    ).limit(top.value).all()
    
    # Convert to response
    data = [
        BestSellingProductResponse(
            id=r.id,
            name=r.name,
            thumbnail=r.thumbnail,
            category_id=r.category_id,
            brand_id=r.brand_id,
            total_sold=int(r.total_sold or 0),
            total_revenue=float(r.total_revenue or 0)
        )
        for r in results
    ]
    
    return BaseResponse(
        success=True,
        message=f"Lấy top {top.value} sản phẩm bán chạy thành công.",
        data=data
    )


@router.get("/products/summary", response_model=BaseResponse[ProductStatisticsResponse])
def get_product_statistics_summary(
    top: TopFilter = Query(TopFilter.top_5, description="Số lượng top sản phẩm"),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin"))
):
    """
    Thống kê tổng quan sản phẩm (Admin only)
    
    Returns:
    - total_products: Tổng số sản phẩm
    - total_active_products: Số sản phẩm đang hoạt động  
    - total_sold_items: Tổng số lượng đã bán
    - total_revenue: Tổng doanh thu
    - best_selling: Top sản phẩm bán chạy
    """
    # Tổng sản phẩm
    total_products = db.query(func.count(Product.id)).filter(
        Product.deleted_at.is_(None)
    ).scalar() or 0
    
    # Sản phẩm active
    total_active = db.query(func.count(Product.id)).filter(
        Product.deleted_at.is_(None),
        Product.is_active == True
    ).scalar() or 0
    
    # Tổng số lượng đã bán
    total_sold = db.query(func.coalesce(func.sum(ProductType.sold), 0)).scalar() or 0
    
    # Tổng doanh thu
    total_revenue = db.query(
        func.coalesce(
            func.sum(ProductType.sold * func.coalesce(ProductType.discount_price, ProductType.price)),
            0
        )
    ).scalar() or 0
    
    # Best selling
    best_selling_results = db.query(
        Product.id,
        Product.name,
        Product.thumbnail,
        Product.category_id,
        Product.brand_id,
        func.coalesce(func.sum(ProductType.sold), 0).label('total_sold'),
        func.coalesce(
            func.sum(ProductType.sold * func.coalesce(ProductType.discount_price, ProductType.price)),
            0
        ).label('total_revenue')
    ).outerjoin(
        ProductType, Product.id == ProductType.product_id
    ).filter(
        Product.deleted_at.is_(None),
        Product.is_active == True
    ).group_by(
        Product.id
    ).order_by(
        desc('total_sold')
    ).limit(top.value).all()
    
    best_selling = [
        BestSellingProductResponse(
            id=r.id,
            name=r.name,
            thumbnail=r.thumbnail,
            category_id=r.category_id,
            brand_id=r.brand_id,
            total_sold=int(r.total_sold or 0),
            total_revenue=float(r.total_revenue or 0)
        )
        for r in best_selling_results
    ]
    
    return BaseResponse(
        success=True,
        message="Lấy thống kê sản phẩm thành công.",
        data=ProductStatisticsResponse(
            total_products=total_products,
            total_active_products=total_active,
            total_sold_items=int(total_sold),
            total_revenue=float(total_revenue),
            best_selling=best_selling
        )
    )
