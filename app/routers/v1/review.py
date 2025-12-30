from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.dependencies.database import get_db
from app.schemas.response.base import BaseResponse
from app.schemas.response.review import ReviewResponse
from app.services.review_service import ReviewService
from app.schemas.request.review import ReviewCreate, ReviewUpdate

router = APIRouter()

@router.post("/", response_model=BaseResponse[ReviewResponse])
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    service = ReviewService(db)
    new_review = service.create(review)
    return BaseResponse(success=True, message="Tạo review thành công.", data=new_review)

@router.get("/{review_id}", response_model=BaseResponse[ReviewResponse])
def get_review(review_id: str, db: Session = Depends(get_db)):
    service = ReviewService(db)
    rv = service.get(review_id)
    if not rv:
        return BaseResponse(success=False, message="Review không tồn tại.", data=None)
    return BaseResponse(success=True, message="Lấy thông tin review thành công.", data=rv)

@router.put("/{review_id}", response_model=BaseResponse[ReviewResponse])
def update_review(review_id: str, review: ReviewUpdate, db: Session = Depends(get_db)):
    service = ReviewService(db)
    updated = service.update(review_id, review)
    if not updated:
        return BaseResponse(success=False, message="Review không tồn tại hoặc không thể cập nhật.", data=None)
    return BaseResponse(success=True, message="Cập nhật review thành công.", data=updated)

@router.delete("/{review_id}", response_model=BaseResponse[bool])
def delete_review(review_id: str, db: Session = Depends(get_db)):
    service = ReviewService(db)
    deleted = service.delete(review_id)
    if not deleted:
        return BaseResponse(success=False, message="Review không tồn tại hoặc đã xóa.", data=False)
    return BaseResponse(success=True, message="Xóa review thành công.", data=True)

@router.get("/product/{product_id}", response_model=BaseResponse[List[ReviewResponse]])
def get_reviews_by_product(product_id: str, db: Session = Depends(get_db)):
    service = ReviewService(db)
    reviews = service.get_by_product(product_id)
    return BaseResponse(success=True, message="Lấy danh sách review theo sản phẩm thành công.", data=reviews)