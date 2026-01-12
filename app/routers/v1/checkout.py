from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.response.base import BaseResponse
from app.schemas.request.checkout import (
    CheckoutPreviewRequest,
    CreateOrderRequest,
    ValidateVoucherRequest
)
from app.schemas.response.checkout import (
    CheckoutPreviewResponse,
    CreateOrderResponse,
    ValidateVoucherResponse,
    PaymentStatusResponse
)
from app.services.checkout_service import CheckoutService
from app.services.sepay_service import SePayService
from app.models.order import Order


router = APIRouter()


@router.post("/preview", response_model=BaseResponse[CheckoutPreviewResponse])
def preview_checkout(
    request: CheckoutPreviewRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Xem trước đơn hàng trước khi thanh toán.
    
    - Tính tổng tiền từ các items đã chọn
    - Validate và áp dụng voucher (nếu có)
    - Tính phí vận chuyển
    """
    try:
        service = CheckoutService(db)
        preview = service.preview_order(
            items=request.items,
            voucher_code=request.voucher_code,
            user_id=current_user.id
        )
        return BaseResponse(
            success=True,
            message="Xem trước đơn hàng thành công.",
            data=preview
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/validate-voucher", response_model=BaseResponse[ValidateVoucherResponse])
def validate_voucher(
    request: ValidateVoucherRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Validate mã voucher.
    
    - Kiểm tra mã tồn tại
    - Kiểm tra còn lượt sử dụng
    - Kiểm tra điều kiện đơn hàng tối thiểu
    - Trả về số tiền giảm giá
    """
    service = CheckoutService(db)
    valid, discount_amount, message = service.validate_voucher(
        code=request.code,
        subtotal=request.subtotal,
        user_id=current_user.id
    )
    
    return BaseResponse(
        success=True,
        message=message,
        data=ValidateVoucherResponse(
            valid=valid,
            discount_amount=discount_amount,
            message=message
        )
    )


@router.post("/create-order", response_model=BaseResponse[CreateOrderResponse])
def create_order(
    request: CreateOrderRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Tạo đơn hàng mới.
    
    - Validate địa chỉ giao hàng
    - Validate và áp dụng voucher
    - Trừ stock sản phẩm
    - Xóa cart items đã đặt
    - Nếu SEPAY: trả về QR code thanh toán
    - Nếu COD: đơn hàng pending chờ giao
    """
    try:
        checkout_service = CheckoutService(db)
        
        order = checkout_service.create_order(
            user_id=current_user.id,
            items=request.items,
            address_id=request.address_id,
            payment_method=request.payment_method,
            voucher_code=request.voucher_code,
            note=request.note
        )
        
        # Tạo thông báo cho admin về đơn hàng mới
        try:
            from app.services.notification_service import notify_admins_new_order
            customer_name = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email
            notify_admins_new_order(
                db=db,
                order_id=str(order.id),
                customer_name=customer_name,
                total_amount=order.final_amount,
                created_by=str(current_user.id)
            )
            print(f"✅ Notification created for order {order.id}")
        except Exception as notif_error:
            # Log lỗi nhưng không fail order creation
            print(f"❌ Error creating notification: {notif_error}")
            import traceback
            traceback.print_exc()
        
        # Nếu thanh toán SePay, tạo QR URL
        payment_url = None
        payment_content = None
        if request.payment_method.upper() == "SEPAY":
            sepay_service = SePayService()
            # Debug: in ra config để kiểm tra
            print(f"SePay Config: acc={sepay_service.account_number}, bank={sepay_service.bank_id}")
            payment_info = sepay_service.generate_payment_info(
                order_id=order.id,
                amount=order.final_amount
            )
            payment_url = payment_info["qr_url"]
            payment_content = payment_info.get("content")
            print(f"Generated payment_url: {payment_url}")
        
        return BaseResponse(
            success=True,
            message="Đặt hàng thành công!" if request.payment_method.upper() == "COD" else "Vui lòng thanh toán để hoàn tất đơn hàng.",
            data=CreateOrderResponse(
                order_id=order.id,
                status=order.status,
                payment_method=order.payment_method,
                total_amount=order.total_amount,
                discount_amount=order.discount_amount,
                final_amount=order.final_amount,
                payment_url=payment_url,
                payment_content=payment_content,
                created_at=order.created_at
            )
        )
    except Exception as e:
        import traceback
        print(f"Create order error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/payment-status/{order_id}", response_model=BaseResponse[PaymentStatusResponse])
def get_payment_status(
    order_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Kiểm tra trạng thái thanh toán của đơn hàng"""
    service = CheckoutService(db)
    status_data = service.get_order_payment_status(order_id)
    
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đơn hàng."
        )
    
    return BaseResponse(
        success=True,
        message="Lấy trạng thái thanh toán thành công.",
        data=status_data
    )


@router.get("/payment-info/{order_id}")
def get_payment_info(
    order_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lấy thông tin thanh toán SePay cho đơn hàng.
    
    Trả về QR code và thời gian còn lại để thanh toán.
    Nếu hết thời gian, trả về lỗi.
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đơn hàng."
        )
    
    if order.payment_method != "SEPAY":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Đơn hàng không phải thanh toán SePay."
        )
    
    # Kiểm tra đơn hàng đã hết thời gian thanh toán chưa
    checkout_service = CheckoutService(db)
    if checkout_service.is_payment_expired(order):
        # Tự động hủy đơn hàng hết hạn
        checkout_service.update_payment_status(order_id, "cancelled")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Đơn hàng đã hết thời gian thanh toán."
        )
    
    # Lấy thời gian còn lại
    remaining_seconds = checkout_service.get_payment_remaining_time(order)
    
    sepay_service = SePayService()
    payment_info = sepay_service.generate_payment_info(
        order_id=order.id,
        amount=order.final_amount
    )
    
    return BaseResponse(
        success=True,
        message="Lấy thông tin thanh toán thành công.",
        data={
            "order_id": order.id,
            "final_amount": order.final_amount,
            "remaining_seconds": remaining_seconds,
            **payment_info
        }
    )


@router.patch("/change-payment-method/{order_id}")
def change_payment_method(
    order_id: str,
    new_method: str,  # Query param: COD hoặc SEPAY
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Đổi phương thức thanh toán cho đơn hàng chưa thanh toán.
    
    - Tạo Payment mới với method mới
    - Đánh dấu Payment cũ là failed
    - Nếu đổi sang SEPAY: trả về QR URL
    """
    checkout_service = CheckoutService(db)
    result = checkout_service.change_payment_method(order_id, current_user.id, new_method)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    # Nếu đổi sang SEPAY, trả về QR URL
    payment_url = None
    payment_content = None
    if new_method.upper() == "SEPAY":
        order = db.query(Order).filter(Order.id == order_id).first()
        sepay_service = SePayService()
        payment_info = sepay_service.generate_payment_info(
            order_id=order.id,
            amount=order.final_amount
        )
        payment_url = payment_info["qr_url"]
        payment_content = payment_info.get("content")
    
    return BaseResponse(
        success=True,
        message=result["message"],
        data={
            "order_id": order_id,
            "payment_method": new_method.upper(),
            "payment_url": payment_url,
            "payment_content": payment_content
        }
    )


@router.post("/cancel-order/{order_id}")
def cancel_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Hủy đơn hàng - User chỉ có thể hủy đơn COD chưa được admin xác nhận.
    
    Điều kiện:
    - Payment method = COD
    - Order status = pending
    """
    checkout_service = CheckoutService(db)
    result = checkout_service.cancel_order(order_id, current_user.id)
    
    return BaseResponse(
        success=result["success"],
        message=result["message"],
        data=None
    )


@router.post("/sepay-webhook")
async def sepay_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook nhận callback từ SePay khi có giao dịch.
    
    SePay sẽ gọi endpoint này khi có tiền chuyển vào tài khoản.
    Payload mẫu:
    {
        "id": 123,
        "gateway": "MB",
        "transactionDate": "2024-01-06",
        "accountNumber": "0123456789",
        "content": "DH12345678",
        "transferAmount": 500000,
        "referenceCode": "TXN123"
    }
    """
    try:
        # Đọc payload
        payload = await request.body()
        payload_str = payload.decode('utf-8')
        
        # Verify signature (TẠM THỜI BỎ QUA cho development)
        # TODO: Enable lại khi deploy production
        sepay_service = SePayService()
        signature = request.headers.get("X-SePay-Signature", "")
        if sepay_service.webhook_secret and signature:
            if not sepay_service.verify_webhook_signature(payload_str, signature):
                print(f"WARNING: SePay signature mismatch. Signature: {signature}")
                # Tạm thời không reject, chỉ log warning
                # raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse JSON
        import json
        data = json.loads(payload_str)
        
        content = data.get("content", "")
        amount = data.get("transferAmount", 0)
        transaction_id = data.get("referenceCode") or str(data.get("id", ""))
        
        # Parse order_id từ content (format: DH{8_chars})
        order_short_id = sepay_service.parse_webhook_content(content)
        if not order_short_id:
            return {"success": False, "message": "Invalid content format"}
        
        # Tìm order có id kết thúc bằng 8 ký tự này
        order = db.query(Order).filter(
            Order.id.like(f"%{order_short_id.lower()}%")
        ).first()
        
        if not order:
            # Thử tìm với dạng có dấu gạch ngang
            order = db.query(Order).filter(
                Order.id.contains(order_short_id.lower())
            ).first()
        
        if not order:
            return {"success": False, "message": "Order not found"}
        
        # Kiểm tra số tiền
        if abs(amount - order.final_amount) > 1000:  # Cho phép sai lệch 1000đ
            return {"success": False, "message": "Amount mismatch"}
        
        # Cập nhật trạng thái
        checkout_service = CheckoutService(db)
        checkout_service.update_payment_status(
            order_id=order.id,
            status="success",
            transaction_id=transaction_id
        )
        
        return {"success": True, "message": "Payment confirmed", "order_id": order.id}
        
    except Exception as e:
        print(f"SePay webhook error: {e}")
        return {"success": False, "message": str(e)}
