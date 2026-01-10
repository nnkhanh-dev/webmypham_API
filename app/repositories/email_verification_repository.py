from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.email_verifications import EmailVerification
from app.repositories.base import BaseRepository


class EmailVerificationRepository(BaseRepository[EmailVerification]):
    """Repository để quản lý email verification"""

    def __init__(self, db: Session):
        super().__init__(EmailVerification, db)

    def get_active_by_user_id(self, user_id: str) -> Optional[EmailVerification]:
        """
        Lấy email verification đang active của user
        
        Args:
            user_id: ID của user
            
        Returns:
            EmailVerification nếu tìm thấy, None nếu không
        """
        return self.db.query(EmailVerification).filter(
            and_(
                EmailVerification.user_id == user_id,
                EmailVerification.is_active == True,
                EmailVerification.verified == False,
                EmailVerification.expires_at > datetime.utcnow()
            )
        ).first()

    def deactivate_all_by_user_id(self, user_id: str) -> None:
        """
        Vô hiệu hóa tất cả email verification của user
        
        Args:
            user_id: ID của user
        """
        self.db.query(EmailVerification).filter(
            EmailVerification.user_id == user_id
        ).update({"is_active": False})
        self.db.commit()

    def increment_attempts(self, verification_id: str) -> EmailVerification:
        """
        Tăng số lần nhập sai
        
        Args:
            verification_id: ID của verification record
            
        Returns:
            EmailVerification đã cập nhật
        """
        verification = self.get_by_id(verification_id)
        if verification:
            verification.attempts += 1
            self.db.commit()
            self.db.refresh(verification)
        return verification

    def mark_as_verified(self, verification_id: str) -> EmailVerification:
        """
        Đánh dấu đã xác thực thành công
        
        Args:
            verification_id: ID của verification record
            
        Returns:
            EmailVerification đã cập nhật
        """
        verification = self.get(verification_id)
        if verification:
            verification.verified = True
            verification.is_active = False
            self.db.commit()
            self.db.refresh(verification)
        return verification

    def create_verification(
        self,
        user_id: str,
        code_hash: str,
        expires_at: datetime,
        created_by: Optional[str] = None
    ) -> EmailVerification:
        """
        Tạo email verification mới
        
        Args:
            user_id: ID của user
            code_hash: Hash của mã 6 số
            expires_at: Thời gian hết hạn
            created_by: ID người tạo
            
        Returns:
            EmailVerification mới
        """
        data = {
            "user_id": user_id,
            "code_hash": code_hash,
            "expires_at": expires_at,
            "last_sent_at": datetime.utcnow(),
            "attempts": 0,
            "resend_count": 0,
            "verified": False,
            "is_active": True
        }
        return self.create(data, created_by=created_by)

    def increment_resend_count(self, user_id: str) -> int:
        """
        Tăng resend_count cho user
        
        Args:
            user_id: ID của user
            
        Returns:
            Số lần resend hiện tại
        """
        # Lấy verification gần nhất (kể cả không active)
        verification = self.db.query(EmailVerification).filter(
            EmailVerification.user_id == user_id
        ).order_by(EmailVerification.created_at.desc()).first()
        
        if verification:
            return verification.resend_count
        return 0
