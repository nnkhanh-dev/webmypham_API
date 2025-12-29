from pydantic import BaseModel
from typing import Optional

class ReviewCreate(BaseModel):
    product_id: str
    user_id: str
    rating: int
    comment: Optional[str] = None

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None