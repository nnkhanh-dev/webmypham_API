from typing import List
from fastapi import APIRouter, HTTPException, status
from app.services.vietnam_administrative_service import (
    load_administrative_data,
    get_provinces,
    get_districts,
    get_wards,
)
from app.schemas.response.base import BaseResponse
from app.schemas.response.administrative import ProvinceResponse, DistrictResponse, WardResponse

router = APIRouter()


@router.get("/provinces", response_model=BaseResponse[List[ProvinceResponse]])
async def get_provinces_endpoint():
    """Lấy danh sách tỉnh/thành phố"""
    try:
        data = await load_administrative_data()
        provinces_data = get_provinces(data)
        if not provinces_data:
            return BaseResponse(success=False, message="Không tìm thấy dữ liệu. Vui lòng chạy script download_hanhchinhvn.py để tải dữ liệu.", data=[])
        provinces = [ProvinceResponse(**p) for p in provinces_data]
        return BaseResponse(success=True, message="OK", data=provinces)
    except Exception as e:
        return BaseResponse(success=False, message=f"Đã xảy ra lỗi: {str(e)}", data=[])


@router.get("/districts", response_model=BaseResponse[List[DistrictResponse]])
async def get_districts_endpoint(province_code: str):
    """Lấy danh sách quận/huyện theo tỉnh"""
    try:
        data = await load_administrative_data()
        districts_data = get_districts(data, province_code)
        districts = [DistrictResponse(**d) for d in districts_data]
        return BaseResponse(success=True, message="OK", data=districts)
    except Exception as e:
        return BaseResponse(success=False, message=f"Đã xảy ra lỗi: {str(e)}", data=[])


@router.get("/wards", response_model=BaseResponse[List[WardResponse]])
async def get_wards_endpoint(province_code: str, district_code: str):
    """Lấy danh sách phường/xã theo quận/huyện"""
    try:
        data = await load_administrative_data()
        wards_data = get_wards(data, province_code, district_code)
        wards = [WardResponse(**w) for w in wards_data]
        return BaseResponse(success=True, message="OK", data=wards)
    except Exception as e:
        return BaseResponse(success=False, message=f"Đã xảy ra lỗi: {str(e)}", data=[])

