from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class BrandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    image_path: Optional[str] = None
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    image_path: Optional[str] = None
    description: Optional[str] = None


class ProductTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    image_path: Optional[str] = None
    price: Optional[float] = None
    status: Optional[str] = None
    discount_price: Optional[float] = None
    quantity: Optional[int] = None
    stock: Optional[int] = None
    volume: Optional[str] = None
    ingredients: Optional[str] = None
    usage: Optional[str] = None
    skin_type: Optional[str] = None
    origin: Optional[str] = None
    type_value_id: Optional[str] = None


class ProductDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    is_active: bool
    brand: Optional[BrandResponse] = None
    category: Optional[CategoryResponse] = None
    product_types: List[ProductTypeResponse] = []


# --- Schemas cho API lấy danh sách biến thể ---

class TypeValueInVariant(BaseModel):
    """Thông tin biến thể (màu sắc, dung tích...)"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str


class ProductVariantResponse(BaseModel):
    """Thông tin chi tiết 1 biến thể sản phẩm"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    price: Optional[float] = None
    discount_price: Optional[float] = None
    stock: Optional[int] = None
    image_path: Optional[str] = None
    volume: Optional[str] = None
    skin_type: Optional[str] = None
    origin: Optional[str] = None
    status: Optional[str] = None
    type_value: Optional[TypeValueInVariant] = None
    is_available: bool = True  # True nếu còn hàng


class ProductVariantsListResponse(BaseModel):
    """Danh sách biến thể của 1 sản phẩm"""
    product_id: str
    product_name: str
    product_thumbnail: Optional[str] = None
    variants: List[ProductVariantResponse] = []