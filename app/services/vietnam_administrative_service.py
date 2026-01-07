import httpx
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

HANHCHINHVN_DATA_URL = "https://raw.githubusercontent.com/kenzouno1/DiaGioiHanhChinhVN/master/data.json"

# Đường dẫn file JSON local (trong thư mục data)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "hanhchinhvn_data.json"

# Cache để lưu trữ dữ liệu sau khi load
_administrative_data: Optional[Dict] = None


def load_from_local_file() -> Optional[Union[List, Dict]]:
    """Load dữ liệu từ file JSON local"""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading local file: {e}")
    return None


async def load_from_url() -> Optional[Union[List, Dict]]:
    """Load dữ liệu từ URL GitHub"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(HANHCHINHVN_DATA_URL)
            response.raise_for_status()
            data = response.json()
            # Lưu vào file local để dùng lần sau
            DATA_DIR.mkdir(exist_ok=True)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return data
    except Exception as e:
        print(f"Error loading from URL: {e}")
        return None


def _convert_list_to_dict(data_list: List) -> Dict:
    """Convert list format thành dict format để dễ tra cứu"""
    result = {}
    for item in data_list:
        province_code = str(item.get("Id", ""))
        result[province_code] = {
            "name": item.get("Name", ""),
            "name_with_type": item.get("Name", ""),
            "slug": item.get("Name", "").lower().replace(" ", "-"),
            "quan_huyen": {}
        }
        
        # Convert districts
        districts_list = item.get("Districts", [])
        for district in districts_list:
            district_code = str(district.get("Id", ""))
            result[province_code]["quan_huyen"][district_code] = {
                "name": district.get("Name", ""),
                "name_with_type": district.get("Name", ""),
                "slug": district.get("Name", "").lower().replace(" ", "-"),
                "xa_phuong": {}
            }
            
            # Convert wards
            wards_list = district.get("Wards", [])
            for ward in wards_list:
                ward_code = str(ward.get("Id", ""))
                result[province_code]["quan_huyen"][district_code]["xa_phuong"][ward_code] = {
                    "name": ward.get("Name", ""),
                    "name_with_type": ward.get("Name", ""),
                    "slug": ward.get("Name", "").lower().replace(" ", "-")
                }
    
    return result


async def load_administrative_data() -> Dict:
    """Load dữ liệu địa giới hành chính VN từ file local hoặc URL"""
    global _administrative_data
    
    if _administrative_data is not None:
        return _administrative_data
    
    # Ưu tiên load từ file local trước
    raw_data = load_from_local_file()
    
    # Nếu không có file local, load từ URL
    if raw_data is None:
        raw_data = await load_from_url()
    
    # Nếu vẫn không có, trả về dict rỗng
    if raw_data is None:
        print("Warning: No administrative data available")
        _administrative_data = {}
        return _administrative_data
    
    # Convert từ list format sang dict format
    if isinstance(raw_data, list):
        _administrative_data = _convert_list_to_dict(raw_data)
    elif isinstance(raw_data, dict):
        _administrative_data = raw_data
    else:
        print("Warning: Unknown data format")
        _administrative_data = {}
    
    return _administrative_data


def get_provinces(data: Dict) -> List[Dict]:
    if not data:
        return []

    return sorted(
        [
            {
                "code": code,
                "name": info.get("name", ""),
                "name_with_type": info.get("name_with_type", ""),
                "slug": info.get("slug", "")
            }
            for code, info in data.items()
        ],
        key=lambda x: x["name"]
    )


def get_districts(data: Dict, province_code: str) -> List[Dict]:
    if not data or province_code not in data:
        return []

    province_data = data[province_code]
    districts_data = province_data.get("quan_huyen", {})

    return sorted(
        [
            {
                "code": code,
                "name": info.get("name", ""),
                "name_with_type": info.get("name_with_type", ""),
                "slug": info.get("slug", ""),
                "parent_code": province_code
            }
            for code, info in districts_data.items()
        ],
        key=lambda x: x["name"]
    )


def get_wards(data: Dict, province_code: str, district_code: str) -> List[Dict]:
    if not data or province_code not in data:
        return []

    province_data = data[province_code]
    district_data = province_data.get("quan_huyen", {}).get(district_code, {})
    wards_data = district_data.get("xa_phuong", {})

    return sorted(
        [
            {
                "code": code,
                "name": info.get("name", ""),
                "name_with_type": info.get("name_with_type", ""),
                "slug": info.get("slug", ""),
                "parent_code": district_code
            }
            for code, info in wards_data.items()
        ],
        key=lambda x: x["name"]
    )


def get_province_name_by_code(data: Dict, province_code: str) -> Optional[str]:
    """Lấy tên tỉnh/thành phố theo code"""
    if not data or province_code not in data:
        return None
    return data[province_code].get("name", "")


def get_district_name_by_code(data: Dict, province_code: str, district_code: str) -> Optional[str]:
    """Lấy tên quận/huyện theo code"""
    if not data or province_code not in data:
        return None
    province_data = data[province_code]
    district_data = province_data.get("quan_huyen", {}).get(district_code, {})
    return district_data.get("name", "")


def get_ward_name_by_code(data: Dict, province_code: str, district_code: str, ward_code: str) -> Optional[str]:
    """Lấy tên phường/xã theo code"""
    if not data or province_code not in data:
        return None
    province_data = data[province_code]
    district_data = province_data.get("quan_huyen", {}).get(district_code, {})
    ward_data = district_data.get("xa_phuong", {}).get(ward_code, {})
    return ward_data.get("name", "")
