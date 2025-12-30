from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.request.order import OrderCreate
from app.schemas.response.order import OrderResponse
from app.services.order_service import OrderService
from app.dependencies.database import get_db
from app.schemas.response.base import BaseResponse

router = APIRouter()

@router.post("/", response_model=BaseResponse[OrderResponse])
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)):
    try:
        service = OrderService(db)
        order = service.create_order(order_in)
        return BaseResponse(success=True, message="Đặt hàng thành công.", data=order)
    except Exception as e:
        return BaseResponse(success=False, message=str(e), data=None)