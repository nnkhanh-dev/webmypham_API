from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.response.base import BaseResponse
from app.schemas.response.review import ReviewResponse
from app.services.review_service import ReviewService
from app.schemas.request.review import ReviewCreate, ReviewUpdate

router = APIRouter()

@router.post("/", response_model=BaseResponse[ReviewResponse])
def create_review(
    review: ReviewCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Tạo đánh giá mới (yêu cầu đã mua và đơn hàng hoàn thành)"""
    service = ReviewService(db)
    new_review = service.create(review, str(current_user.id))
    return BaseResponse(success=True, message="Đánh giá thành công!", data=new_review)

@router.get("/my-reviewable-products", response_model=BaseResponse[List[dict]])
def get_my_reviewable_products(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lấy danh sách sản phẩm có thể đánh giá (từ đơn hàng đã hoàn thành)"""
    service = ReviewService(db)
    products = service.get_reviewable_products(str(current_user.id))
    return BaseResponse(
        success=True, 
        message=f"Có {len(products)} sản phẩm có thể đánh giá", 
        data=products
    )

@router.get("/{review_id}", response_model=BaseResponse[ReviewResponse])
def get_review(review_id: str, db: Session = Depends(get_db)):
    """Lấy thông tin đánh giá theo ID"""
    service = ReviewService(db)
    rv = service.get(review_id)
    if not rv:
        return BaseResponse(success=False, message="Review không tồn tại.", data=None)
    return BaseResponse(success=True, message="Lấy thông tin review thành công.", data=rv)

@router.put("/{review_id}", response_model=BaseResponse[ReviewResponse])
def update_review(
    review_id: str, 
    review: ReviewUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cập nhật đánh giá (chỉ người tạo mới được sửa)"""
    service = ReviewService(db)
    updated = service.update(review_id, review, str(current_user.id))
    if not updated:
        return BaseResponse(success=False, message="Review không tồn tại hoặc không thể cập nhật.", data=None)
    return BaseResponse(success=True, message="Cập nhật review thành công.", data=updated)

@router.delete("/{review_id}", response_model=BaseResponse[bool])
def delete_review(
    review_id: str, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Xóa đánh giá (chỉ người tạo mới được xóa)"""
    service = ReviewService(db)
    deleted = service.delete(review_id, str(current_user.id))
    if not deleted:
        return BaseResponse(success=False, message="Review không tồn tại hoặc đã xóa.", data=False)
    return BaseResponse(success=True, message="Xóa review thành công.", data=True)

@router.get("/product/{product_id}", response_model=BaseResponse[List[ReviewResponse]])
def get_reviews_by_product(product_id: str, db: Session = Depends(get_db)):
    """Lấy tất cả đánh giá của một sản phẩm"""
    service = ReviewService(db)
    reviews = service.get_by_product(product_id)
    return BaseResponse(success=True, message="Lấy danh sách review theo sản phẩm thành công.", data=reviews)
