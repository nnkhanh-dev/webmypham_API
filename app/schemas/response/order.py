from typing import List, Optional
from pydantic import BaseModel

class OrderItemResponse(BaseModel):
    id: str
    product_type_id: str
    quantity: int
    price: Optional[float] = None

    class Config:
        orm_mode = True

class OrderResponse(BaseModel):
    id: str
    user_id: str
    status: str
    items: List[OrderItemResponse]
    total_amount: float
    discount_amount: Optional[float]
    final_amount: float

    class Config:
        orm_mode = True