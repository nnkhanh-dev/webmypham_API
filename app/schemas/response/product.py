from pydantic import BaseModel
from typing import List, Optional

class BrandResponse(BaseModel):
    id: str
    name: str
    image_path: Optional[str]
    description: Optional[str]
    class Config:
        orm_mode = True

class CategoryResponse(BaseModel):
    id: str
    name: str
    image_path: Optional[str]
    description: Optional[str]
    class Config:
        orm_mode = True

class ProductTypeResponse(BaseModel):
    id: str
    image_path: Optional[str]
    price: Optional[float]
    status: Optional[str]
    discount_price: Optional[float]
    quantity: Optional[int]
    stock: Optional[int]
    volume: Optional[str]
    ingredients: Optional[str]
    usage: Optional[str]
    skin_type: Optional[str]
    origin: Optional[str]
    type_value_id: Optional[str]
    class Config:
        orm_mode = True

class ProductDetailResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    thumbnail: Optional[str]
    is_active: bool
    brand: Optional[BrandResponse]
    category: Optional[CategoryResponse]
    product_types: List[ProductTypeResponse] = []
    class Config:
        orm_mode = True