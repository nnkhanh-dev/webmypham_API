from pydantic import BaseModel
from typing import Optional


class ProvinceResponse(BaseModel):
    code: str
    name: str
    name_with_type: Optional[str] = None
    slug: Optional[str] = None


class DistrictResponse(BaseModel):
    code: str
    name: str
    name_with_type: Optional[str] = None
    slug: Optional[str] = None
    parent_code: Optional[str] = None


class WardResponse(BaseModel):
    code: str
    name: str
    name_with_type: Optional[str] = None
    slug: Optional[str] = None
    parent_code: Optional[str] = None

