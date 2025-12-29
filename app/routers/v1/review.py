from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.schemas.request.review import ReviewCreate, ReviewUpdate
from app.schemas.response.review import ReviewResponse
from app.services.review_service import ReviewService
from typing import List

router = APIRouter()

@router.post("/", response_model=ReviewResponse)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    service = ReviewService(db)
    return service.create(review)

@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: str, db: Session = Depends(get_db)):
    service = ReviewService(db)
    rv = service.get(review_id)
    if not rv:
        raise HTTPException(status_code=404, detail="Review not found")
    return rv

@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(review_id: str, review: ReviewUpdate, db: Session = Depends(get_db)):
    service = ReviewService(db)
    updated = service.update(review_id, review)
    if not updated:
        raise HTTPException(status_code=404, detail="Review not found")
    return updated

@router.delete("/{review_id}")
def delete_review(review_id: str, db: Session = Depends(get_db)):
    service = ReviewService(db)
    if not service.delete(review_id):
        raise HTTPException(status_code=404, detail="Review not found")
    return {"result": True}

@router.get("/product/{product_id}", response_model=List[ReviewResponse])
def get_reviews_by_product(product_id: str, db: Session = Depends(get_db)):
    service = ReviewService(db)
    return service.get_by_product(product_id)