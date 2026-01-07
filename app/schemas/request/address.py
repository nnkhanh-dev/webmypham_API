from pydantic import BaseModel, Field
from typing import Optional


class AddressBase(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    province_code: Optional[str] = Field(None, description="Mã tỉnh/thành phố từ API administrative")
    district_code: Optional[str] = Field(None, description="Mã quận/huyện từ API administrative")
    ward_code: Optional[str] = Field(None, description="Mã phường/xã từ API administrative")
    detail: Optional[str] = Field(None, max_length=255, description="Số nhà, tên đường")
    is_default: Optional[bool] = False


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    province_code: Optional[str] = Field(None, description="Mã tỉnh/thành phố từ API administrative")
    district_code: Optional[str] = Field(None, description="Mã quận/huyện từ API administrative")
    ward_code: Optional[str] = Field(None, description="Mã phường/xã từ API administrative")
    detail: Optional[str] = Field(None, max_length=255, description="Số nhà, tên đường")
    is_default: Optional[bool] = None

