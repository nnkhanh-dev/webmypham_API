"""
Upload Router - API endpoints cho upload file
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List

from app.dependencies.permission import require_roles
from app.schemas.response.base import BaseResponse
from app.services.upload_product_service import save_upload_file, get_upload_url

router = APIRouter()


class UploadResponse:
    filename: str
    url: str


@router.post("/image", response_model=BaseResponse)
async def upload_image(
    file: UploadFile = File(..., description="File ảnh cần upload"),
    subfolder: str = "products",
    current_user = Depends(require_roles("admin"))
):
    """
    Upload một file ảnh (Admin only)
    
    - **file**: File ảnh (jpg, jpeg, png, gif, webp)
    - **subfolder**: Thư mục con (mặc định: products)
    
    Returns:
        filename: Tên file đã lưu
        url: URL để truy cập file
    """
    saved_filename = await save_upload_file(file, subfolder)
    
    return BaseResponse(
        success=True,
        message="Upload thành công.",
        data={
            "filename": saved_filename,
            "url": get_upload_url(saved_filename)
        }
    )


@router.post("/images", response_model=BaseResponse)
async def upload_multiple_images(
    files: List[UploadFile] = File(..., description="Danh sách file ảnh"),
    subfolder: str = "products",
    current_user = Depends(require_roles("admin"))
):
    """
    Upload nhiều file ảnh cùng lúc (Admin only)
    
    - **files**: Danh sách file ảnh
    - **subfolder**: Thư mục con (mặc định: products)
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Chỉ được upload tối đa 10 file")
    
    results = []
    for file in files:
        saved_filename = await save_upload_file(file, subfolder)
        results.append({
            "filename": saved_filename,
            "url": get_upload_url(saved_filename)
        })
    
    return BaseResponse(
        success=True,
        message=f"Upload thành công {len(results)} file.",
        data=results
    )
