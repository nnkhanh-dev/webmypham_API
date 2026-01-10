from pydantic import BaseModel
from typing import Optional


class TypeValueResponse(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


class ProductTypeDetailResponse(BaseModel):
    id: str
    product_id: str
    type_value_id: Optional[str]
    image_path: Optional[str]
    price: Optional[float]
    discount_price: Optional[float]
    status: Optional[str]
    quantity: Optional[int]
    stock: Optional[int]
    volume: Optional[str]
    ingredients: Optional[str]
    usage: Optional[str]
    skin_type: Optional[str]
    origin: Optional[str]
    sold: Optional[int]

    type_value: Optional[TypeValueResponse]

    class Config:
        from_attributes = True
