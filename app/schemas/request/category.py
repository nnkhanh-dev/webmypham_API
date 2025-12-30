from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    image_path: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None)
    parent_id: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    image_path: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[str] = None


class CategoryInDBBase(CategoryBase):
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


class CategoryResponse(CategoryInDBBase):
    children: Optional[List["CategoryResponse"]] = None


CategoryResponse.update_forward_refs()
