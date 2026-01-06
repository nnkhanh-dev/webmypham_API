from pydantic import BaseModel, Field
from typing import Optional, List


class ProductTypeCreateRequest(BaseModel):
    """Schema để tạo ProductType kèm theo Product"""
    price: Optional[float] = Field(None, ge=0, description="Giá sản phẩm")
    discount_price: Optional[float] = Field(None, ge=0, description="Giá khuyến mãi")
    quantity: Optional[int] = Field(None, ge=0, description="Số lượng")
    stock: Optional[int] = Field(None, ge=0, description="Số lượng tồn kho")
    volume: Optional[str] = Field(None, max_length=50, description="Dung tích (VD: 50ml)")
    ingredients: Optional[str] = Field(None, description="Thành phần")
    usage: Optional[str] = Field(None, description="Cách sử dụng")
    skin_type: Optional[str] = Field(None, max_length=100, description="Loại da phù hợp")
    origin: Optional[str] = Field(None, max_length=100, description="Xuất xứ")
    image_path: Optional[str] = Field(None, max_length=255, description="Đường dẫn hình ảnh")
    type_value_id: Optional[str] = Field(None, description="ID loại giá trị")
    status: Optional[str] = Field("active", max_length=50, description="Trạng thái")


class ProductTypeUpdateRequest(BaseModel):
    """Schema để cập nhật ProductType"""
    id: Optional[str] = Field(None, description="ID của ProductType (nếu cập nhật existing)")
    price: Optional[float] = Field(None, ge=0)
    discount_price: Optional[float] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    volume: Optional[str] = Field(None, max_length=50)
    ingredients: Optional[str] = None
    usage: Optional[str] = None
    skin_type: Optional[str] = Field(None, max_length=100)
    origin: Optional[str] = Field(None, max_length=100)
    image_path: Optional[str] = Field(None, max_length=255)
    type_value_id: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)


class ProductCreateRequest(BaseModel):
    """Schema để tạo Product mới"""
    name: str = Field(..., min_length=1, max_length=200, description="Tên sản phẩm")
    brand_id: Optional[str] = Field(None, description="ID thương hiệu")
    category_id: Optional[str] = Field(None, description="ID danh mục")
    description: Optional[str] = Field(None, max_length=255, description="Mô tả sản phẩm")
    thumbnail: Optional[str] = Field(None, max_length=255, description="Đường dẫn thumbnail")
    is_active: bool = Field(True, description="Trạng thái hoạt động")
    product_types: Optional[List[ProductTypeCreateRequest]] = Field(
        default=[], description="Danh sách các loại sản phẩm"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Kem dưỡng ẩm",
                "brand_id": "uuid-brand-id",
                "category_id": "uuid-category-id",
                "description": "Kem dưỡng ẩm cao cấp từ Hàn Quốc",
                "thumbnail": "/images/products/kem-duong.jpg",
                "is_active": True,
                "product_types": [
                    {
                        "price": 350000,
                        "discount_price": 299000,
                        "volume": "50ml",
                        "stock": 100,
                        "origin": "Hàn Quốc"
                    }
                ]
            }
        }


class ProductUpdateRequest(BaseModel):
    """Schema để cập nhật Product"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Tên sản phẩm")
    brand_id: Optional[str] = Field(None, description="ID thương hiệu")
    category_id: Optional[str] = Field(None, description="ID danh mục")
    description: Optional[str] = Field(None, max_length=255, description="Mô tả sản phẩm")
    thumbnail: Optional[str] = Field(None, max_length=255, description="Đường dẫn thumbnail")
    is_active: Optional[bool] = Field(None, description="Trạng thái hoạt động")
    product_types: Optional[List[ProductTypeUpdateRequest]] = Field(
        None, description="Danh sách các loại sản phẩm cần cập nhật"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Kem dưỡng ẩm - Updated",
                "description": "Mô tả mới cho sản phẩm",
                "is_active": True
            }
        }
