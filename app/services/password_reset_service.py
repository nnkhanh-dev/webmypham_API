"""
Service cho chức năng quên mật khẩu / reset password.

Flow:
1. User nhập email -> tạo token reset -> gửi email kèm link
2. User click link -> đến trang reset password với token
3. User nhập mật khẩu mới -> verify token -> update password -> xóa token
4. User click lại link cũ -> token đã xóa -> redirect 404
"""

import secrets
from datetime import datetime, timedelta
from typing import Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService
from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class PasswordResetService:
    """Service xử lý forgot password và reset password"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.email_service = EmailService()
        self.token_expiry_hours = 1  # Token hết hạn sau 1 giờ
    
    def generate_reset_token(self) -> str:
        """
        Tạo token ngẫu nhiên an toàn.
        Sử dụng secrets.token_urlsafe để tạo token phù hợp cho URL.
        
        Returns:
            Token string (URL-safe)
        """
        return secrets.token_urlsafe(32)
    
    def request_password_reset(self, email: str) -> Tuple[bool, str]:
        """
        Xử lý yêu cầu reset password.
        - Kiểm tra email có tồn tại không
        - Tạo reset token
        - Lưu token vào DB
        - Gửi email kèm link reset
        
        Args:
            email: Email của user
            
        Returns:
            Tuple (success: bool, message: str)
        """
        # Tìm user theo email
        user = self.user_repo.get_by_email(email)
        
        if not user:
            # Security: Không tiết lộ email không tồn tại
            # Trả về success = True để tránh enumerate user
            return True, "Nếu email tồn tại, chúng tôi đã gửi link reset password đến email của bạn."
        
        # Kiểm tra email đã verified chưa
        if not user.email_confirmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email chưa được xác thực. Vui lòng xác thực email trước khi reset password."
            )
        
        # Tạo reset token
        reset_token = self.generate_reset_token()
        
        # Lưu token vào DB
        user.reset_password_token = reset_token
        self.db.commit()
        
        # Tạo link reset password
        # Format: http://localhost:5173/reset-password?token=abc123
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        # Gửi email
        email_sent = self._send_reset_email(user.email, reset_link, user.first_name)
        
        if not email_sent:
            # Rollback nếu gửi email thất bại
            user.reset_password_token = None
            self.db.commit()
            return False, "Không thể gửi email. Vui lòng thử lại sau."
        
        return True, "Link reset password đã được gửi đến email của bạn. Vui lòng kiểm tra hộp thư."
    
    def verify_reset_token(self, token: str) -> Tuple[bool, str, object]:
        """
        Xác thực reset token.
        
        Args:
            token: Reset token từ URL
            
        Returns:
            Tuple (is_valid: bool, message: str, user: User or None)
        """
        if not token:
            return False, "Token không hợp lệ.", None
        
        # Tìm user có token này
        user = self.user_repo.get_by_reset_token(token)
        
        if not user:
            return False, "Token không hợp lệ hoặc đã hết hạn.", None
        
        # Token hợp lệ
        return True, "Token hợp lệ.", user
    
    def reset_password(
        self, 
        token: str, 
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Reset password với token.
        - Verify token
        - Hash password mới
        - Update vào DB
        - Xóa token
        - Xóa refresh token (bắt user login lại)
        
        Args:
            token: Reset token
            new_password: Mật khẩu mới
            
        Returns:
            Tuple (success: bool, message: str)
        """
        # 1. Verify token
        is_valid, message, user = self.verify_reset_token(token)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # 2. Hash password mới
        hashed_password = pwd_context.hash(new_password)
        
        # 3. Update password và xóa token
        user.password_hash = hashed_password
        user.reset_password_token = None  # Xóa token sau khi dùng
        user.refresh_token = None  # Xóa refresh token (bắt login lại)
        
        # 4. Commit changes
        self.db.commit()
        
        # 5. Gửi email thông báo password đã đổi (optional)
        self._send_password_changed_email(user.email, user.first_name)
        
        return True, "Mật khẩu đã được đặt lại thành công. Vui lòng đăng nhập với mật khẩu mới."
    
    def _send_reset_email(self, email: str, reset_link: str, first_name: str = None) -> bool:
        """
        Gửi email chứa link reset password.
        
        Args:
            email: Email người nhận
            reset_link: Link reset password
            first_name: Tên người dùng (optional)
            
        Returns:
            True nếu gửi thành công, False nếu thất bại
        """
        subject = "Yêu cầu đặt lại mật khẩu - BeautyStore"
        
        greeting = f"Xin chào {first_name}," if first_name else "Xin chào,"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Đặt lại mật khẩu</h1>
                </div>
                <div class="content">
                    <p>{greeting}</p>
                    
                    <p>Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.</p>
                    
                    <p>Nhấn vào nút bên dưới để đặt lại mật khẩu:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Đặt lại mật khẩu</a>
                    </div>
                    
                    <p>Hoặc copy link sau vào trình duyệt:</p>
                    <p style="background: white; padding: 10px; border-radius: 5px; word-break: break-all;">
                        {reset_link}
                    </p>
                    
                    <div class="warning">
                        <strong>⚠️ Lưu ý:</strong>
                        <ul>
                            <li>Link này chỉ sử dụng được <strong>1 lần</strong></li>
                            <li>Link sẽ hết hạn sau <strong>{self.token_expiry_hours} giờ</strong></li>
                            <li>Sau khi đặt lại mật khẩu, link này sẽ không còn hiệu lực</li>
                        </ul>
                    </div>
                    
                    <p>Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.</p>
                    
                    <p>Trân trọng,<br><strong>BeautyStore Team</strong></p>
                </div>
                <div class="footer">
                    <p>Email này được gửi tự động, vui lòng không trả lời.</p>
                    <p>&copy; 2026 BeautyStore. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.email_service.send_email(email, subject, html_content)
    
    def _send_password_changed_email(self, email: str, first_name: str = None) -> bool:
        """
        Gửi email thông báo mật khẩu đã được thay đổi.
        
        Args:
            email: Email người nhận
            first_name: Tên người dùng (optional)
            
        Returns:
            True nếu gửi thành công, False nếu thất bại
        """
        subject = "Mật khẩu đã được thay đổi - BeautyStore"
        
        greeting = f"Xin chào {first_name}," if first_name else "Xin chào,"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .success {{ background: #d4edda; border-left: 4px solid #28a745; padding: 10px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Mật khẩu đã được thay đổi</h1>
                </div>
                <div class="content">
                    <p>{greeting}</p>
                    
                    <div class="success">
                        <p><strong>Mật khẩu của bạn đã được thay đổi thành công!</strong></p>
                    </div>
                    
                    <p>Nếu bạn không thực hiện thay đổi này, vui lòng liên hệ với chúng tôi ngay lập tức.</p>
                    
                    <p>Trân trọng,<br><strong>BeautyStore Team</strong></p>
                </div>
                <div class="footer">
                    <p>Email này được gửi tự động, vui lòng không trả lời.</p>
                    <p>&copy; 2026 BeautyStore. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.email_service.send_email(email, subject, html_content)
