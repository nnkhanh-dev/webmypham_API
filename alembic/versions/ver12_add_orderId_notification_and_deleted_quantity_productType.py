"""add orderId, is_global to Notification, fix content type, add is_read to user_notifications

Revision ID: ver12
Revises: ver11
Create Date: 2026-01-10 13:13:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'ver12'
down_revision: Union[str, None] = 'ver11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add order_id column to notifications
    op.add_column(
        'notifications',
        sa.Column('order_id', sa.String(length=100), nullable=True)
    )
    # Add is_global column to notifications
    op.add_column(
        'notifications',
        sa.Column('is_global', sa.Integer(), nullable=True)
    )
    # Fix content column type from Boolean/Integer to Text
    op.alter_column(
        'notifications',
        'content',
        existing_type=sa.Boolean(),
        type_=sa.Text(),
        existing_nullable=True
    )
    # Add is_read column to user_notifications
    op.add_column(
        'user_notifications',
        sa.Column('is_read', sa.Boolean(), nullable=True, default=False)
    )
    # Add read_at column to user_notifications
    op.add_column(
        'user_notifications',
        sa.Column('read_at', sa.DateTime(), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('user_notifications', 'read_at')
    op.drop_column('user_notifications', 'is_read')
    op.alter_column(
        'notifications',
        'content',
        existing_type=sa.Text(),
        type_=sa.Boolean(),
        existing_nullable=True
    )
    op.drop_column('notifications', 'is_global')
    op.drop_column('notifications', 'order_id')