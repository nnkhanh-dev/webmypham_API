"""
Seed script để tạo dữ liệu mẫu cho Notifications
Chạy: python seed_notifications.py
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Thêm thư mục gốc project vào path
project_root = os.path.dirname(os.path.abspath(__file__))
if 'scripts' in project_root:
    project_root = os.path.dirname(project_root)
sys.path.insert(0, project_root)

from app.core.database import SessionLocal
from app.models.notification import Notification
from app.models.userNotification import UserNotification
from app.models.user import User
from app.models.role import Role
from app.models.userRole import UserRole


def get_admin_users(db):
    """Lấy danh sách admin users"""
    admin_role = db.query(Role).filter(
        Role.name.ilike("admin"),
        Role.deleted_at.is_(None)
    ).first()
    
    if not admin_role:
        return []
    
    return db.query(User).join(
        UserRole, User.id == UserRole.user_id
    ).filter(
        UserRole.role_id == admin_role.id,
        User.deleted_at.is_(None)
    ).all()


def seed_notifications(db):
    """Tạo dữ liệu Notification mẫu"""
    
    # Kiểm tra đã có notifications chưa
    existing = db.query(Notification).count()
    if existing > 0:
        print(f"  - Đã có {existing} notifications, bỏ qua")
        return 0
    
    admin_users = get_admin_users(db)
    if not admin_users:
        print("  ! Không tìm thấy admin users")
        return 0
    
    notifications_data = [
        {
            "title": "🛒 Đơn hàng mới #DH001",
            "content": "Khách hàng Nguyễn Văn A vừa đặt đơn hàng trị giá 450,000đ",
            "type": "order",
            "days_ago": 0,
            "is_read": False
        },
        {
            "title": "🛒 Đơn hàng mới #DH002",
            "content": "Khách hàng Trần Thị B vừa đặt đơn hàng trị giá 890,000đ",
            "type": "order",
            "days_ago": 0,
            "is_read": False
        },
        {
            "title": "🛒 Đơn hàng mới #DH003",
            "content": "Khách hàng Lê Văn C vừa đặt đơn hàng trị giá 1,250,000đ",
            "type": "order",
            "days_ago": 1,
            "is_read": False
        },
        {
            "title": "📦 Sản phẩm sắp hết hàng",
            "content": "Son Thỏi Love M.O.I màu #01 chỉ còn 5 sản phẩm",
            "type": "system",
            "days_ago": 1,
            "is_read": True
        },
        {
            "title": "🛒 Đơn hàng mới #DH004",
            "content": "Khách hàng Phạm Thị D vừa đặt đơn hàng trị giá 320,000đ",
            "type": "order",
            "days_ago": 2,
            "is_read": True
        },
        {
            "title": "⭐ Đánh giá mới",
            "content": "Khách hàng đã đánh giá 5 sao cho sản phẩm Phấn Nước Iconic",
            "type": "system",
            "days_ago": 2,
            "is_read": True
        },
        {
            "title": "🛒 Đơn hàng mới #DH005",
            "content": "Khách hàng Hoàng Văn E vừa đặt đơn hàng trị giá 580,000đ",
            "type": "order",
            "days_ago": 3,
            "is_read": True
        },
        {
            "title": "🎁 Voucher sắp hết hạn",
            "content": "Voucher NEWYEAR2026 sẽ hết hạn trong 7 ngày",
            "type": "promotion",
            "days_ago": 5,
            "is_read": True
        },
    ]
    
    created_count = 0
    for data in notifications_data:
        created_at = datetime.utcnow() - timedelta(days=data["days_ago"])
        
        notification = Notification(
            title=data["title"],
            content=data["content"],
            type=data["type"],
            is_global=False,
            created_at=created_at,
            updated_at=created_at
        )
        db.add(notification)
        db.flush()
        
        # Gửi notification đến tất cả admin
        for admin in admin_users:
            user_notification = UserNotification(
                user_id=admin.id,
                notification_id=notification.id,
                is_read=data["is_read"],
                read_at=created_at if data["is_read"] else None,
                created_at=created_at,
                updated_at=created_at
            )
            db.add(user_notification)
        
        created_count += 1
        status = "✓" if data["is_read"] else "○"
        print(f"  + [{status}] {data['title'][:40]}...")
    
    db.commit()
    return created_count


def main():
    print("\n" + "="*50)
    print("🔔 BEAUTY STORE - SEED NOTIFICATIONS")
    print("="*50 + "\n")
    
    db = SessionLocal()
    
    try:
        print("📦 Đang tạo Notifications...")
        count = seed_notifications(db)
        
        print("\n" + "="*50)
        print("✅ SEED HOÀN TẤT!")
        print(f"   - Notifications mới: {count}")
        print("\n📋 Trạng thái:")
        print("   ○ = Chưa đọc")
        print("   ✓ = Đã đọc")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
