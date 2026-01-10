"""add sold column to product_types table

Revision ID: ver8
Revises: ver7
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'ver8'
down_revision = 'ver7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Kiểm tra xem cột sold đã tồn tại chưa
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('product_types')]
    
    if 'sold' not in columns:
        # Chỉ thêm cột nếu chưa tồn tại
        op.add_column('product_types', sa.Column('sold', sa.Integer(), nullable=True, server_default='0'))


def downgrade() -> None:
    # Kiểm tra xem cột sold có tồn tại không
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('product_types')]
    
    if 'sold' in columns:
        # Chỉ xóa cột nếu tồn tại
        op.drop_column('product_types', 'sold')

