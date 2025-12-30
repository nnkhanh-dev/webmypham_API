from typing import List, Optional
from pydantic import BaseModel

class OrderItemCreate(BaseModel):
    product_type_id: str
    quantity: int

class OrderCreate(BaseModel):
    user_id: str
    items: List[OrderItemCreate]
    # có thể thêm các thông tin shipping, note, voucher, etc nếu muốn
    voucher_code: Optional[str] = None
    note: Optional[str] = None