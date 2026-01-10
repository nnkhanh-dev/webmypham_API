import random
import string
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.models.email_verifications import EmailVerification
from app.models.user import User
from app.repositories.email_verification_repository import EmailVerificationRepository
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService


# Cấu hình hash cho code
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Cấu hình giới hạn
MAX_ATTEMPTS = 5  # Số lần nhập sai tối đa
MAX_RESEND = 5  # Số lần resend tối đa
CODE_EXPIRY_MINUTES = 10  # Thời gian hết hạn của code (10 phút)
RESEND_COOLDOWN_SECONDS = 60  # Thời gian chờ giữa các lần resend (60 giây)


class EmailVerificationService:
    """Service xử lý logic email verification"""

    def __init__(self, db: Session):
        self.db = db
        self.verification_repo = EmailVerificationRepository(db)
        self.user_repo = UserRepository(db)

    @staticmethod
    def generate_code() -> str:
        """
        Generate mã 6 số ngẫu nhiên
        
        Returns:
            Chuỗi 6 số
        """
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    def hash_code(code: str) -> str:
        """
        Hash mã verification
        
        Args:
            code: Mã 6 số
            
        Returns:
            Hash của mã
        """
        return pwd_context.hash(code)

    @staticmethod
    def verify_code(plain_code: str, hashed_code: str) -> bool:
        """
        Kiểm tra mã có khớp không
        
        Args:
            plain_code: Mã nhập vào
            hashed_code: Mã đã hash
            
        Returns:
            True nếu khớp
        """
        try:
            return pwd_context.verify(plain_code, hashed_code)
        except Exception:
            return False

    def send_verification_code(
        self, 
        user_id: str, 
        is_resend: bool = False
    ) -> Tuple[bool, str]:
        """
        Gửi mã xác thực qua email
        
        Args:
            user_id: ID của user
            is_resend: True nếu là resend
            
        Returns:
            Tuple (success, message)
        """
        # 1. Lấy thông tin user
        user = self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User không tồn tại"
            )

        # 2. Kiểm tra đã verify chưa
        if user.email_confirmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được xác thực"
            )

        # 3. Nếu là resend, kiểm tra giới hạn
        if is_resend:
            # Kiểm tra cooldown
            active_verification = self.verification_repo.get_active_by_user_id(user_id)
            if active_verification and active_verification.last_sent_at:
                time_since_last_send = (datetime.utcnow() - active_verification.last_sent_at).total_seconds()
                if time_since_last_send < RESEND_COOLDOWN_SECONDS:
                    remaining = int(RESEND_COOLDOWN_SECONDS - time_since_last_send)
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Vui lòng đợi {remaining} giây trước khi gửi lại"
                    )

            # Kiểm tra số lần resend
            current_resend_count = self.verification_repo.increment_resend_count(user_id)
            if current_resend_count >= MAX_RESEND:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Đã vượt quá số lần gửi lại cho phép ({MAX_RESEND} lần)"
                )

        # 4. Vô hiệu hóa tất cả code cũ
        self.verification_repo.deactivate_all_by_user_id(user_id)

        # 5. Tạo mã mới
        code = self.generate_code()
        code_hash = self.hash_code(code)
        expires_at = datetime.utcnow() + timedelta(minutes=CODE_EXPIRY_MINUTES)

        # 6. Lấy resend_count từ lần gửi trước (nếu có)
        previous_resend_count = self.verification_repo.increment_resend_count(user_id)
        new_resend_count = previous_resend_count + 1 if is_resend else 0

        # 7. Lưu vào database
        verification_data = {
            "user_id": user_id,
            "code_hash": code_hash,
            "expires_at": expires_at,
            "last_sent_at": datetime.utcnow(),
            "attempts": 0,
            "resend_count": new_resend_count,
            "verified": False,
            "is_active": True
        }
        self.verification_repo.create(verification_data, created_by=user_id)

        # 8. Gửi email
        user_name = f"{user.first_name} {user.last_name}".strip() if user.first_name or user.last_name else None
        email_sent = EmailService.send_verification_code(user.email, code, user_name)

        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Không thể gửi email. Vui lòng thử lại sau"
            )

        return True, f"Mã xác thực đã được gửi đến {user.email}"

    def send_verification_code_by_email(
        self, 
        email: str, 
        is_resend: bool = False
    ) -> Tuple[bool, str]:
        """
        Gửi mã xác thực qua email (dùng email thay vì user_id)
        
        Args:
            email: Email của user
            is_resend: True nếu là resend
            
        Returns:
            Tuple (success, message)
        """
        # Lấy user bằng email
        user = self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email không tồn tại trong hệ thống"
            )
        
        # Gọi hàm gửi code bằng user_id
        return self.send_verification_code(user.id, is_resend)

    def verify_email(self, user_id: str, code: str) -> Tuple[bool, str]:
        """
        Xác thực email bằng code
        
        Args:
            user_id: ID của user
            code: Mã 6 số nhập vào
            
        Returns:
            Tuple (success, message)
        """
        # 1. Lấy user
        user = self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User không tồn tại"
            )

        # 2. Kiểm tra đã verify chưa
        if user.email_confirmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được xác thực"
            )
        

        # 3. Lấy và kiểm tra verification hợp lệ
        verification = self.verification_repo.get_active_by_user_id(user_id)
        if not verification or verification.expires_at < datetime.utcnow():
            # Vô hiệu hóa nếu có verification nhưng đã hết hạn
            if verification:
                verification.is_active = False
                self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã xác thực không hợp lệ hoặc đã hết hạn. Vui lòng yêu cầu gửi lại"
            )

        # 4. Kiểm tra số lần nhập sai
        if verification.attempts >= MAX_ATTEMPTS:
            verification.is_active = False
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Đã vượt quá số lần nhập sai ({MAX_ATTEMPTS} lần). Vui lòng yêu cầu gửi lại"
            )

        # 5. Verify code
        is_valid = self.verify_code(code, verification.code_hash)
        
        if not is_valid:
            # Tăng số lần nhập sai
            verification.attempts += 1
            self.db.commit()
            
            remaining_attempts = MAX_ATTEMPTS - verification.attempts
            if remaining_attempts <= 0:
                verification.is_active = False
                self.db.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mã không chính xác. Đã hết số lần thử. Vui lòng yêu cầu gửi lại"
                )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã không chính xác. Còn {remaining_attempts} lần thử"
            )

        # 7. Verify thành công
        # Cập nhật verification
        self.verification_repo.mark_as_verified(verification.id)
        
        # Cập nhật user
        user.email_confirmed = True
        self.db.commit()

        return True, "Xác thực email thành công"

    def verify_email_by_email(self, email: str, code: str) -> Tuple[bool, str]:
        """
        Xác thực email bằng code (dùng email thay vì user_id)
        
        Args:
            email: Email của user
            code: Mã 6 số nhập vào
            
        Returns:
            Tuple (success, message)
        """
        # Lấy user bằng email
        user = self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email không tồn tại trong hệ thống"
            )
        
        # Gọi hàm verify bằng user_id
        return self.verify_email(user.id, code)

    def get_verification_status(self, user_id: str) -> dict:
        """
        Lấy trạng thái verification của user
        
        Args:
            user_id: ID của user
            
        Returns:
            Dict chứa thông tin trạng thái
        """
        user = self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User không tồn tại"
            )

        if user.email_confirmed:
            return {
                "verified": True,
                "email": user.email
            }

        verification = self.verification_repo.get_active_by_user_id(user_id)
        
        if not verification:
            return {
                "verified": False,
                "has_active_code": False,
                "email": user.email
            }

        # Kiểm tra hết hạn
        is_expired = verification.expires_at < datetime.utcnow()
        
        return {
            "verified": False,
            "has_active_code": not is_expired,
            "email": user.email,
            "expires_at": verification.expires_at.isoformat() if not is_expired else None,
            "attempts_remaining": MAX_ATTEMPTS - verification.attempts if not is_expired else 0,
            "resend_count": verification.resend_count
        }
