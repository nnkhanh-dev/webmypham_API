"""recalculate order financial totals

Revision ID: ver10
Revises: ver9
Create Date: 2026-01-07 20:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

# --- PHẦN KHAI BÁO BẮT BUỘC ---
revision = 'ver10'
down_revision = 'ver9'
branch_labels = None
depends_on = None

def update_order_totals(connection):
    """Hàm xử lý logic tính toán tiền của bạn"""
    session = Session(bind=connection)
    
    # 1. Lấy tất cả đơn hàng hiện có
    # Sử dụng sa.text để chạy raw SQL an toàn
    orders = session.execute(sa.text("SELECT id, voucher_id FROM orders")).fetchall()
    
    for order in orders:
        order_id = order.id
        voucher_id = order.voucher_id
        
        # 2. Tính Subtotal (Tổng tiền hàng) từ order_details
        subtotal_result = session.execute(
            sa.text("SELECT SUM(price * number) FROM order_details WHERE order_id = :oid"),
            {"oid": order_id}
        ).scalar()
        
        subtotal = float(subtotal_result) if subtotal_result else 0.0
        discount_amount = 0.0
        
        # 3. Tính toán Discount từ Voucher (nếu có)
        if voucher_id is not None:  # Kiểm tra voucher_id có tồn tại không
            voucher = session.execute(
                sa.text("SELECT discount, min_order_amount, max_discount FROM vouchers WHERE id = :vid"),
                {"vid": voucher_id}
            ).fetchone()
            
            if voucher and subtotal >= (voucher.min_order_amount or 0):
                # Giả định voucher.discount là số phần trăm (VD: 10.0 = 10%)
                potential_discount = subtotal * (voucher.discount / 100)
                
                # Áp dụng mức giảm tối đa (cap) nếu có
                max_discount = voucher.max_discount
                if max_discount is not None and potential_discount > max_discount:
                    discount_amount = max_discount
                else:
                    discount_amount = potential_discount

        # 4. Tính Final Amount
        final_amount = max(subtotal - discount_amount, 0)
        
        # 5. Cập nhật lại vào bảng orders
        session.execute(
            sa.text("""
                UPDATE orders 
                SET total_amount = :subtotal, 
                    discount_amount = :discount, 
                    final_amount = :final
                WHERE id = :oid
            """),
            {
                "subtotal": subtotal,
                "discount": discount_amount,
                "final": final_amount,
                "oid": order_id
            }
        )
    
    session.commit()

def upgrade():
    # Khi chạy alembic upgrade head, hàm này sẽ được gọi
    connection = op.get_bind()
    print("🚀 Đang tính toán lại dòng tiền cho toàn bộ đơn hàng...")
    update_order_totals(connection)
    print("✅ Hoàn thành cập nhật ver9!")

def downgrade():
    # Thường với data fix chúng ta không cần rollback tiền về 0
    pass