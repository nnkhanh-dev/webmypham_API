from pydantic import BaseModel, ConfigDict, computed_field
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
    sold: Optional[int] = None
    type_value: Optional["TypeValueResponse"] = None
    
    @computed_field
    @property
    def is_available(self) -> bool:
        """Kiểm tra còn hàng dựa trên stock"""
        return self.stock is not None and self.stock > 0


# Thông tin type_value và type cho product type
class TypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str

class TypeValueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    type: Optional[TypeResponse] = None


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


# --- Schemas cho Homepage Product List ---

class ProductCardResponse(BaseModel):
    """Thông tin sản phẩm hiển thị dạng card trên homepage"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    brand_name: Optional[str] = None
    category_name: Optional[str] = None
    # Price info (từ product_types)
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_discount_price: Optional[float] = None
    # Rating info
    avg_rating: Optional[float] = None
    review_count: Optional[int] = 0
    # Stats
    total_sold: Optional[int] = 0
    favorite_count: Optional[int] = 0


class ProductListResponse(BaseModel):
    """Response cho danh sách sản phẩm (homepage sections)"""
    items: List[ProductCardResponse] = []
    total: int = 0