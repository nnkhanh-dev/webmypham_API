# app/core/config.py
from functools import lru_cache
from typing import List, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Cấu hình đọc file .env
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" 
    )

    # --- Database Configuration ---
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # --- Security & JWT ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60
    
    # --- Server Configuration ---
    DEBUG: bool = False
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000
    RELOAD: bool = True

    # --- CORS Configuration ---
    CORS_ORIGINS: Any = [] 

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            # Xử lý chuỗi "url1,url2" thành list
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # --- SePay Configuration ---
    SEPAY_ACCOUNT_NUMBER: str = ""
    SEPAY_ACCOUNT_NAME: str = ""
    SEPAY_BANK_ID: str = "MB"
    SEPAY_TEMPLATE: str = "compact2"
    SEPAY_WEBHOOK_SECRET: str = ""

    # --- Mail Configuration (SMTP) ---
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

# Sử dụng lru_cache để đảm bảo Settings chỉ được khởi tạo một lần (Singleton pattern)
@lru_cache
def get_settings() -> Settings:
    return Settings()

# Tạo đối tượng settings để sử dụng toàn dự án
settings = get_settings()