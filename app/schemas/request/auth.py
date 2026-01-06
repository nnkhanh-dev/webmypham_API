from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator
import re


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

    @validator("password")
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @validator("first_name", "last_name")
    def strip_names(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if isinstance(v, str) else v

    @validator("phone_number")
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        digits = "".join([c for c in v if c.isdigit()])
        if len(digits) not in (10, 11):
            raise ValueError("phone_number must contain 10 or 11 digits")
        if not digits.startswith("0"):
            raise ValueError("phone_number must start with '0'")
        return digits


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    name: Optional[str] = None
    dob: Optional[datetime] = None
    gender: Optional[int] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str