from datetime import timedelta, datetime
from typing import Optional, Tuple
import secrets

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.schemas.request.auth import UserCreate
from app.core.security import create_access_token
from app.core.config import settings
from app.services.email_verification_service import EmailVerificationService

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def create_tokens_for_user(user: User, db: Session) -> dict:
    # Access Token
    access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_payload = {
        "sub": str(user.id),
        "email": user.email,
        "type": "access",
    }

    access_token, _ = create_access_token(access_payload, expires_delta=access_expires)

    # Refresh Token
    refresh_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_payload = {
        "sub": str(user.id),
        "email": user.email,
        "type": "refresh",
    }

    refresh_token, _ = create_access_token(
        refresh_payload, expires_delta=refresh_expires
    )

    # Rotate refresh token
    user.refresh_token = refresh_token
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "scope": ",".join([r.name for r in getattr(user, "roles", [])]),
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_expires_in": settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    user_repo = UserRepository(db)
    return user_repo.get_by_email(email)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def create_user(
    db: Session,
    user_in: UserCreate,
    role_name: str = "CLIENT",
    created_by: Optional[str] = None,
) -> User:
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)

    hashed = pwd_context.hash(user_in.password)
    user_data = {
        "email": user_in.email,
        "password_hash": hashed,
        "first_name": user_in.first_name,
        "last_name": user_in.last_name,
        "phone_number": user_in.phone_number,
        "email_confirmed": False,  # Mặc định chưa xác thực email
    }
    user = user_repo.create(user_data, created_by=created_by)
    role = role_repo.get_or_create(role_name, created_by=created_by)
    user = user_repo.assign_role(user, role.name)

    # Gửi mã xác thực email
    try:
        verification_service = EmailVerificationService(db)
        verification_service.send_verification_code(user.id, is_resend=False)
    except Exception as e:
        # Log error nhưng không fail registration
        print(f"Warning: Failed to send verification email: {str(e)}")

    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    is_valid = verify_password(password, getattr(user, "password_hash", ""))
    if not is_valid:
        return None

    # Strict Mode: Block unverified users from logging in
    if not user.email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email chưa được xác thực. Vui lòng kiểm tra email và nhập mã xác thực.",
        )

    return user


# --- THÊM MỚI ---


def login(user: User, db: Session) -> dict:
    """Tạo cặp Access/Refresh token và lưu Refresh token vào DB"""

    # 1. Tạo Access Token (Ngắn hạn - ví dụ 15p)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_payload = {"sub": str(user.id), "email": user.email, "type": "access"}
    access_token, _ = create_access_token(
        access_token_payload, expires_delta=access_token_expires
    )

    # 2. Tạo Refresh Token (Dài hạn - 60p)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "type": "refresh",
    }
    # Tái sử dụng hàm create_access_token nhưng thời gian dài hơn
    refresh_token, _ = create_access_token(
        refresh_token_payload, expires_delta=refresh_token_expires
    )

    # 3. Lưu Refresh Token vào DB (User Model)
    user.refresh_token = refresh_token
    db.add(user)
    db.commit()
    db.refresh(user)

    # 4. Chuẩn bị dữ liệu trả về
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "scope": (
            ",".join([r.name for r in getattr(user, "roles", [])])
            if getattr(user, "roles", None)
            else ""
        ),
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_expires_in": settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


def renew_tokens(refresh_token: str, db: Session) -> dict:
    """Xác thực refresh token cũ và cấp cặp token mới"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Decode token
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # 2. Kiểm tra User trong DB
    user_repo = UserRepository(db)
    user = user_repo.get_with_roles(
        user_id
    )  # Dùng hàm get_with_roles để lấy cả roles nếu cần

    if not user:
        raise credentials_exception

    # 3. Bảo mật: So sánh token gửi lên với token đang lưu trong DB
    # Nếu khác nhau -> Có thể token đã bị revoke hoặc bị đánh cắp -> Chặn
    if user.refresh_token != refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token (Revoked or Reused)",
        )

    # 4. Tạo cặp token mới (Rotate)
    return create_tokens_for_user(user, db)


def authenticate_google_user(google_id_token: str, db: Session) -> User:
    """
    Xác thực Google ID Token và tạo hoặc lấy user từ DB.

    Args:
        google_id_token: ID token từ Google OAuth
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: Nếu token không hợp lệ
    """
    try:
        # Verify token với Google
        idinfo = id_token.verify_oauth2_token(
            google_id_token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10,  # Cho phép lệch tối đa 10 giây
        )

        # Kiểm tra issuer
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")

        # Lấy thông tin user từ token
        email = idinfo.get("email")
        given_name = idinfo.get("given_name", "")
        family_name = idinfo.get("family_name", "")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not found in Google token",
            )

    except ValueError as e:
        # Token không hợp lệ
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}",
        )

    # Tìm hoặc tạo user trong DB
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(email)

    if not user:
        # Tạo user mới nếu chưa tồn tại
        # Google OAuth không có password nên set password_hash là hash của random string
        # để đảm bảo không ai có thể login bằng password với tài khoản Google
        role_repo = RoleRepository(db)
        random_password = secrets.token_urlsafe(32)  # Random 32-byte string
        user_data = {
            "email": email,
            "password_hash": pwd_context.hash(
                random_password
            ),  # Hash của random string
            "first_name": given_name,
            "last_name": family_name,
            "phone_number": None,
            "email_confirmed": True,  # Google OAuth users auto-verified
        }
        user = user_repo.create(user_data, created_by="google_oauth")

        # Gán role CLIENT
        role = role_repo.get_or_create("CLIENT", created_by="google_oauth")
        user = user_repo.assign_role(user, role.name)

    return user
