from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BrandBase(BaseModel):
    name: str = Field(..., max_length=100)
    image_path: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=255)


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    image_path: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=255)


class BrandInDBBase(BrandBase):
    id: str
    slug: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class BrandResponse(BrandInDBBase):
    pass
