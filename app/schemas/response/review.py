from pydantic import BaseModel
from typing import Optional

class ReviewResponse(BaseModel):
    id: str
    product_id: str
    user_id: str
    order_id: Optional[str] = None
    rating: int
    comment: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    user_name: Optional[str] = None  # Tên người đánh giá

    class Config:
        orm_mode = True
