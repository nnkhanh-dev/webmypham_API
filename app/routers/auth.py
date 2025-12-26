from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.core.security import create_access_token
from app.services.auth_service import authenticate_user, create_user, get_user_by_email
from app.schemas.auth import UserCreate, UserResponse, TokenResponse, LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def login_for_access_token(login: LoginRequest, db: Session = Depends(get_db)):
    # JSON login using email + password
    user = authenticate_user(db, login.email, login.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    # build scope string from user's roles and include user info in token payload
    role_names = [r.name for r in getattr(user, "roles", [])]
    scope_str = " ".join(role_names) if role_names else ""
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "roles": role_names,
    }
    token, expire = create_access_token(payload, scopes=scope_str)
    expires_in = int((expire - datetime.utcnow()).total_seconds())
    return {
        "access_token": token,
        "token_type": "bearer",
        "scope": scope_str,
        "expires_at": expire.replace(microsecond=0).isoformat() + "Z",
        "expires_in": max(expires_in, 0),
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # validate password length to avoid bcrypt 72-byte limit
    if len(user_in.password.encode("utf-8")) > 72:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password too long (max 72 bytes)")

    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = create_user(db, user_in)
    return user


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user = Depends(get_current_user)):
    return current_user


# Note: `/auth/token` now accepts JSON body {"email":..., "password":...}.