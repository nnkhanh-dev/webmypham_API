"""
SePay Integration Service
SePay là cổng thanh toán QR Code tự động cho Việt Nam

Hướng dẫn:
1. Đăng ký tài khoản tại https://sepay.vn
2. Lấy API Key từ dashboard
3. Cấu hình webhook URL để nhận callback

Flow:
1. Tạo QR code với nội dung chuyển khoản chuẩn
2. User quét QR và chuyển tiền
3. SePay webhook gửi callback khi nhận được tiền
4. Server cập nhật trạng thái đơn hàng
"""
import hashlib
import hmac
import re
from datetime import datetime
from typing import Optional

from app.core.config import settings


class SePayService:
    def __init__(self):
        self.account_number = settings.SEPAY_ACCOUNT_NUMBER
        self.account_name = settings.SEPAY_ACCOUNT_NAME
        self.bank_id = settings.SEPAY_BANK_ID
        self.template = settings.SEPAY_TEMPLATE
        self.webhook_secret = settings.SEPAY_WEBHOOK_SECRET

    def generate_payment_content(self, order_id: str) -> str:
        """Tạo nội dung chuyển khoản duy nhất để định danh đơn hàng"""
        # Format: DH + 8 ký tự cuối của order_id
        short_id = order_id.replace("-", "")[-8:].upper()
        return f"DH{short_id}"

    def generate_qr_url(self, order_id: str, amount: float) -> str:
        """
        Tạo URL QR Code thanh toán từ SePay
        
        SePay QR URL format: https://qr.sepay.vn/img?acc={account}&bank={bank}&amount={amount}&des={content}
        Khi dùng QR của SePay, SePay sẽ theo dõi giao dịch và bắn webhook khi thanh toán thành công.
        """
        content = self.generate_payment_content(order_id)
        
        # Sử dụng QR của SePay (qr.sepay.vn)
        qr_url = (
            f"https://qr.sepay.vn/img"
            f"?acc={self.account_number}"
            f"&bank={self.bank_id}"
            f"&amount={int(amount)}"
            f"&des={content}"
        )
        
        return qr_url

    def generate_payment_info(self, order_id: str, amount: float) -> dict:
        """Tạo thông tin thanh toán đầy đủ"""
        content = self.generate_payment_content(order_id)
        
        return {
            "bank_id": self.bank_id,
            "account_number": self.account_number,
            "account_name": self.account_name,
            "amount": amount,
            "content": content,
            "qr_url": self.generate_qr_url(order_id, amount),
            "expire_at": None  # Có thể thêm thời hạn thanh toán
        }

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Xác thực webhook signature từ SePay
        
        SePay gửi webhook với header X-SePay-Signature
        Signature = HMAC-SHA256(payload, webhook_secret)
        """
        if not self.webhook_secret:
            return True  # Bỏ qua nếu chưa cấu hình
        
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)

    def parse_webhook_content(self, content: str) -> Optional[str]:
        """
        Parse nội dung chuyển khoản để lấy order_id
        Content format có thể là:
        - DH{8_chars}
        - 113570317763-01664933757-DH{8_chars}
        """

        content = content.upper().strip()
        
        # Tìm pattern DH + 8 ký tự hex/alphanum ở BẤT KỲ vị trí nào
        match = re.search(r'DH([A-Z0-9]{8})', content)
        if match:
            return match.group(1)  # Trả về 8 ký tự sau DH
        
        return None
