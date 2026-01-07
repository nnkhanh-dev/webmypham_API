from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from app.models.address import Address
from app.repositories.address_repository import AddressRepository
from app.schemas.request.address import AddressCreate, AddressUpdate
from app.services.vietnam_administrative_service import (
    load_administrative_data,
    get_province_name_by_code,
    get_district_name_by_code,
    get_ward_name_by_code,
)
from fastapi import HTTPException, status


async def _resolve_administrative_names(province_code: Optional[str], district_code: Optional[str], ward_code: Optional[str], validate: bool = True) -> dict:
    result = {"province": None, "district": None, "ward": None}
    
    if not province_code:
        return result
    
    try:
        data = await load_administrative_data()
        
        province_name = get_province_name_by_code(data, province_code)
        if validate and not province_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã tỉnh/thành phố '{province_code}' không hợp lệ"
            )
        result["province"] = province_name
        
        if district_code:
            if not province_name:
                if validate:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Không thể tìm quận/huyện vì mã tỉnh/thành phố '{province_code}' không hợp lệ"
                    )
                return result
                
            district_name = get_district_name_by_code(data, province_code, district_code)
            if validate and not district_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Mã quận/huyện '{district_code}' không thuộc tỉnh/thành phố '{province_code}' hoặc không hợp lệ"
                )
            result["district"] = district_name
            
            if ward_code:
                if not district_name:
                    if validate:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Không thể tìm phường/xã vì mã quận/huyện '{district_code}' không hợp lệ"
                        )
                    return result
                    
                ward_name = get_ward_name_by_code(data, province_code, district_code, ward_code)
                if validate and not ward_name:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Mã phường/xã '{ward_code}' không thuộc quận/huyện '{district_code}' hoặc không hợp lệ"
                    )
                result["ward"] = ward_name
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error resolving administrative names: {e}")
        if validate:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Lỗi khi tra cứu địa giới hành chính"
            )
    
    return result


async def create_address(db: Session, user_id: str, address_in: AddressCreate, created_by: Optional[str] = None) -> Address:
    """Tạo địa chỉ mới cho user"""
    repo = AddressRepository(db)
    
    # Nếu đặt làm mặc định, bỏ đặt các địa chỉ mặc định khác
    if address_in.is_default:
        repo.unset_all_defaults(user_id)
    
    data = address_in.dict(exclude_unset=True)
    
    names = await _resolve_administrative_names(
        data.get("province_code"),
        data.get("district_code"),
        data.get("ward_code")
    )
    
    if names["province"]:
        data["province"] = names["province"]
    if names["district"]:
        data["district"] = names["district"]
    if names["ward"]:
        data["ward"] = names["ward"]
    
    data.pop("province_code", None)
    data.pop("district_code", None)
    data.pop("ward_code", None)
    
    data["user_id"] = user_id
    return repo.create(data, created_by=created_by)


def get_address(db: Session, address_id: str, user_id: str) -> Optional[Address]:
    """Lấy một địa chỉ của user"""
    repo = AddressRepository(db)
    address = repo.get_by_user(user_id, address_id)
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    return address


def list_addresses(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> Tuple[List[Address], int]:
    """Lấy danh sách địa chỉ của user"""
    repo = AddressRepository(db)
    return repo.list_by_user(user_id, skip=skip, limit=limit)


async def update_address(db: Session, address_id: str, user_id: str, address_in: AddressUpdate, updated_by: Optional[str] = None) -> Optional[Address]:
    """Cập nhật địa chỉ"""
    repo = AddressRepository(db)
    
    address = repo.get_by_user(user_id, address_id)
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    data = address_in.dict(exclude_unset=True)
    
    if "province_code" in data or "district_code" in data or "ward_code" in data:
        names = await _resolve_administrative_names(
            data.get("province_code"),
            data.get("district_code"),
            data.get("ward_code")
        )
        
        if names["province"]:
            data["province"] = names["province"]
        if names["district"]:
            data["district"] = names["district"]
        if names["ward"]:
            data["ward"] = names["ward"]
    
    data.pop("province_code", None)
    data.pop("district_code", None)
    data.pop("ward_code", None)
    
    if data.get("is_default") is True:
        repo.unset_all_defaults(user_id)
    
    return repo.update(address_id, data, updated_by=updated_by)


def delete_address(db: Session, address_id: str, user_id: str, deleted_by: Optional[str] = None) -> bool:
    """Xóa địa chỉ"""
    repo = AddressRepository(db)
    
    address = repo.get_by_user(user_id, address_id)
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    return repo.delete(address_id, deleted_by=deleted_by)


def set_default_address(db: Session, address_id: str, user_id: str, updated_by: Optional[str] = None) -> Optional[Address]:
    """Đặt địa chỉ làm mặc định"""
    repo = AddressRepository(db)
    
    address = repo.get_by_user(user_id, address_id)
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    repo.unset_all_defaults(user_id)
    
    return repo.update(address_id, {"is_default": True}, updated_by=updated_by)
