from pydantic import BaseModel, Field
from typing import Optional

class ReviewCreate(BaseModel):
    product_id: str = Field(..., description="ID sản phẩm")
    order_id: str = Field(..., description="ID đơn hàng (bắt buộc để đảm bảo đã mua)")
    rating: int = Field(..., ge=1, le=5, description="Đánh giá từ 1-5 sao")
    comment: Optional[str] = Field(None, max_length=500, description="Nội dung đánh giá")

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)
