from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.pagination import get_pagination
from app.dependencies.permission import require_roles
from app.schemas.request.auth import UserUpdate
from app.schemas.response.auth import UserResponse
from app.schemas.response.user import UserDetailResponse
from app.schemas.response.base import BaseResponse
from app.services.user_service import get_user, list_users, update_user, delete_user

router = APIRouter()

@router.get("/", response_model=BaseResponse[List[UserResponse]])
def list_users_endpoint(params: dict = Depends(get_pagination), db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
    items, total = list_users(db, skip=params.get("skip", 0), limit=params.get("limit", 100), q=params.get("q"))
    meta = {**params, "total": total}
    return BaseResponse(success=True, message="OK", data=items, meta=meta)

@router.get("/me", response_model=BaseResponse[UserDetailResponse])
def get_me(current_user = Depends(get_current_user)):
    return BaseResponse(success=True, message="OK", data=current_user)

@router.put("/me", response_model=BaseResponse[UserDetailResponse])
def update_me(user_in: UserUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    obj = update_user(db, str(current_user.id), user_in, updated_by=str(current_user.id))
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return BaseResponse(success=True, message="Updated", data=obj)

@router.get("/{user_id}", response_model=BaseResponse[UserResponse])
def read_user(user_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    obj = get_user(db, user_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # allow admins or the user themself
    user_roles = [r.name for r in getattr(current_user, "roles", [])]
    if "ADMIN" not in user_roles and str(current_user.id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return BaseResponse(success=True, message="OK", data=obj)

@router.put("/{user_id}", response_model=BaseResponse[UserResponse])
def update_user_endpoint(user_id: str, user_in: UserUpdate, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
    obj = update_user(db, user_id, user_in, updated_by=str(current_user.id) if current_user else None)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return BaseResponse(success=True, message="Updated", data=obj)

@router.delete("/{user_id}", response_model=BaseResponse[None])
def delete_user_endpoint(user_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles("ADMIN"))):
    ok = delete_user(db, user_id, deleted_by=str(current_user.id) if current_user else None)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return BaseResponse(success=True, message="Deleted", data=None)
