from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.request.auth import UserCreate, LoginRequest
from app.schemas.response.auth import UserResponse, TokenResponse
from app.schemas.response.base import BaseResponse
from app.services.auth_service import create_user, authenticate_user
from app.core.security import create_access_token
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=BaseResponse[UserResponse], status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # note: service will hash password and create default role
    user = create_user(db, user_in, created_by=None)
    return BaseResponse(success=True, message="Created", data=user)


@router.post("/token", response_model=TokenResponse)
def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token_data = {"sub": str(user.id), "email": user.email}
    token, expire = create_access_token(token_data, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    token_payload = {
        "access_token": token,
        "token_type": "bearer",
        "scope": ",".join([r.name for r in getattr(user, "roles", [])]) if getattr(user, "roles", None) else "",
        "expires_at": expire.isoformat(),
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
    return TokenResponse(**token_payload)
