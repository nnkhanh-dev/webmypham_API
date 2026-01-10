from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.pagination import get_pagination
from app.dependencies.permission import require_roles
from app.schemas.request.type import (
    TypeCreate,
    TypeUpdate,
    TypeResponse,
    TypeWithValuesResponse,
)
from app.schemas.response.base import BaseResponse
from app.services.type_service import (
    get_type,
    get_types,
    create_type,
    update_type,
    delete_type,
)

router = APIRouter()


@router.get("/", response_model=BaseResponse[List[TypeWithValuesResponse]])
def list_types(params: dict = Depends(get_pagination), db: Session = Depends(get_db), current_user = Depends(require_roles("CLIENT", "ADMIN"))):
    items, total = get_types(
        db,
        skip=params.get("skip", 0),
        limit=params.get("limit", 100),
        q=params.get("q"),
        sort_by=params.get("sort_by", "id"),
        sort_dir=params.get("sort_dir", "desc"),
    )
    meta = {**params, "total": total}
    return BaseResponse(success=True, message="OK", data=items, meta=meta)


@router.get("/{type_id}", response_model=BaseResponse[TypeResponse])
def read_type(type_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles("CLIENT", "ADMIN"))):
    obj = get_type(db, type_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Type not found")
    return BaseResponse(success=True, message="OK", data=obj)


@router.post("/", response_model=BaseResponse[TypeResponse], status_code=status.HTTP_201_CREATED)
def create_type_endpoint(type_in: TypeCreate, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
    obj = create_type(db, type_in, created_by=str(current_user.id) if current_user else None)
    return BaseResponse(success=True, message="Created", data=obj)


@router.put("/{type_id}", response_model=BaseResponse[TypeResponse])
def update_type_endpoint(type_id: str, type_in: TypeUpdate, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
    obj = update_type(db, type_id, type_in, updated_by=str(current_user.id) if current_user else None)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Type not found")
    return BaseResponse(success=True, message="Updated", data=obj)


@router.delete("/{type_id}", response_model=BaseResponse[None])
def delete_type_endpoint(type_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
    ok = delete_type(db, type_id, deleted_by=str(current_user.id) if current_user else None)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Type not found")
    return BaseResponse(success=True, message="Deleted", data=None)

