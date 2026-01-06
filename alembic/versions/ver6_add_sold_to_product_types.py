"""add sold column to product_types

Revision ID: ver6
Revises: ver5_add_full_name_phone_to_address
Create Date: 2026-01-06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ver6_add_sold_to_product_types'
down_revision = 'ver5_add_full_name_phone_to_address'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Thêm cột sold vào bảng product_types
    op.add_column('product_types', sa.Column('sold', sa.Integer(), nullable=True, server_default='0'))


def downgrade() -> None:
    # Xóa cột sold
    op.drop_column('product_types', 'sold')
