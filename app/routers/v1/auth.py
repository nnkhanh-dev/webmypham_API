from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.request.auth import UserCreate, LoginRequest, RefreshTokenRequest, GoogleLoginRequest
from app.schemas.response.auth import UserResponse, TokenResponse
from app.schemas.response.base import BaseResponse
from app.services.auth_service import create_user, authenticate_user, login, renew_tokens, authenticate_google_user

router = APIRouter()

@router.post("/register", response_model=BaseResponse[UserResponse], status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user_in, created_by=None)
    return BaseResponse(success=True, message="Created", data=user)

@router.post("/login", response_model=TokenResponse)
def authentication(form_data: LoginRequest, db: Session = Depends(get_db)):
    # 1. Xác thực user/pass
    print(form_data.password)

    user = authenticate_user(db, form_data.email, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tài khoản hoặc mật khẩu không đúng!")
    
    # 2. Tạo token và trả về response kèm thông tin user
    # Logic tạo token + lưu refresh token vào DB đã chuyển vào service
    response_data = login(user, db)
    
    return TokenResponse(**response_data)

@router.post("/refresh-token", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    API dùng để lấy access token mới bằng refresh token.
    Đồng thời trả về refresh token mới (Rotate Refresh Token).
    """
    token_data = renew_tokens(request.refresh_token, db)
    return TokenResponse(**token_data)

@router.post("/google", response_model=TokenResponse)
def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    API xác thực Google OAuth.
    Nhận ID token từ Google, verify và tạo/lấy user, sau đó trả về access token và refresh token.
    """
    # 1. Xác thực Google token và lấy/tạo user
    user = authenticate_google_user(request.id_token, db)
    
    # 2. Tạo token và trả về response (giống flow login thông thường)
    response_data = login(user, db)
    
    return TokenResponse(**response_data)