from typing import Generic, Optional, TypeVar, List, Dict
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic.generics import GenericModel

T = TypeVar("T")

class BaseResponse(GenericModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    errors: Optional[List[str]] = None
    meta: Optional[Dict] = None

    model_config = ConfigDict(
        exclude_none=True
    )
