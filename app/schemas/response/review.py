from pydantic import BaseModel
from typing import Optional

class ReviewResponse(BaseModel):
    id: str
    product_id: str
    user_id: str
    rating: int
    comment: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True