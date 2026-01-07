from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Response schema cho kết quả phân trang"""
    items: List[T]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True
