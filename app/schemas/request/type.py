from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TypeBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class TypeCreate(TypeBase):
    pass


class TypeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class TypeInDBBase(TypeBase):
    id: str
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class TypeResponse(TypeInDBBase):
    pass


class TypeValueBase(BaseModel):
    name: str = Field(..., max_length=100)


class TypeValueCreate(TypeValueBase):
    pass


class TypeValueUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)


class TypeValueInDBBase(TypeValueBase):
    id: str
    type_id: str
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class TypeValueResponse(TypeValueInDBBase):
    pass


class TypeWithValuesResponse(TypeInDBBase):
    """Type response with nested type_values"""
    values: List[TypeValueResponse] = []  
    
    class Config:
        orm_mode = True
