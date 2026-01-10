"""update order table add address_id and voucher_id

Revision ID: ver7
Revises: ver6
Create Date: 2026-01-06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ver7'
down_revision = 'ver6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Thêm address_id vào bảng orders
    op.add_column('orders', sa.Column('address_id', sa.String(36), sa.ForeignKey('addresses.id'), nullable=True))
    
    # Thêm voucher_id vào bảng orders
    op.add_column('orders', sa.Column('voucher_id', sa.String(36), sa.ForeignKey('vouchers.id'), nullable=True))
    
    # Thêm payment_method vào bảng orders
    op.add_column('orders', sa.Column('payment_method', sa.String(50), nullable=True))
    
    # Thêm note vào bảng orders
    op.add_column('orders', sa.Column('note', sa.String(500), nullable=True))
    
    # Thêm transaction_id cho SePay
    op.add_column('payments', sa.Column('transaction_id', sa.String(100), nullable=True))
    op.add_column('payments', sa.Column('amount', sa.Float(), nullable=True))
    
    # Xóa bảng order_vouchers (không cần nữa)
    op.drop_table('order_vouchers')


def downgrade() -> None:
    # Tạo lại bảng order_vouchers
    op.create_table('order_vouchers',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('order_id', sa.String(36), sa.ForeignKey('orders.id'), nullable=True),
        sa.Column('voucher_id', sa.String(36), sa.ForeignKey('vouchers.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('updated_by', sa.String(36), nullable=True),
        sa.Column('deleted_by', sa.String(36), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Xóa các cột đã thêm
    op.drop_column('payments', 'amount')
    op.drop_column('payments', 'transaction_id')
    op.drop_column('orders', 'note')
    op.drop_column('orders', 'payment_method')
    op.drop_column('orders', 'voucher_id')
    op.drop_column('orders', 'address_id')
