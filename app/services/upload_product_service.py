"""
Upload Service - Xử lý upload file
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile, HTTPException
import shutil

# Thư mục lưu trữ uploads
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def ensure_upload_dir():
    """Đảm bảo thư mục upload tồn tại"""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def generate_unique_filename(original_filename: str) -> str:
    """
    Tạo tên file unique dựa trên timestamp và UUID
    Format: {timestamp}_{uuid}_{original_name}
    """
    # Lấy extension
    ext = Path(original_filename).suffix.lower()
    
    # Tạo tên file với timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    
    # Lấy tên file gốc (không extension), chuyển thành slug
    original_name = Path(original_filename).stem
    # Giới hạn độ dài và loại bỏ ký tự đặc biệt
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in original_name)[:30]
    
    return f"{timestamp}_{unique_id}_{safe_name}{ext}"


def validate_image(file: UploadFile) -> None:
    """Validate file upload"""
    # Kiểm tra extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # Kiểm tra content type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )


async def save_upload_file(file: UploadFile, subfolder: str = "products") -> str:
    """
    Lưu file upload và trả về tên file đã lưu
    
    Args:
        file: File được upload
        subfolder: Thư mục con (products, avatars, etc.)
    
    Returns:
        Tên file đã lưu (relative path từ uploads): "products/20260107_091332_abc123_image.jpg"
    """
    validate_image(file)
    
    # Tạo thư mục nếu chưa có
    target_dir = UPLOAD_DIR / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Tạo tên file unique
    filename = generate_unique_filename(file.filename)
    filepath = target_dir / filename
    
    # Lưu file
    try:
        with filepath.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not save file: {str(e)}"
        )
    finally:
        file.file.close()
    
    # Trả về relative path
    return f"{subfolder}/{filename}"


async def delete_upload_file(file_path: str) -> bool:
    """
    Xóa file upload
    
    Args:
        file_path: Đường dẫn relative từ uploads folder
    
    Returns:
        True nếu xóa thành công
    """
    try:
        full_path = UPLOAD_DIR / file_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    except Exception:
        return False


def get_upload_url(filename: str) -> str:
    """
    Trả về URL để truy cập file upload
    
    Args:
        filename: Tên file (relative path từ uploads)
    
    Returns:
        URL path: "/uploads/products/20260107_091332_abc123_image.jpg"
    """
    if not filename:
        return None
    return f"/uploads/{filename}"
