"""add sold column to product_types table

Revision ID: ver8
Revises: ver7
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ver8'
down_revision = 'ver7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Thêm cột sold vào bảng product_types
    op.add_column('product_types', sa.Column('sold', sa.Integer(), nullable=True, server_default='0'))


def downgrade() -> None:
    # Xóa cột sold khỏi bảng product_types
    op.drop_column('product_types', 'sold')
