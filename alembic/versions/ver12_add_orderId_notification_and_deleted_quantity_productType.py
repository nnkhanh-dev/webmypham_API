"""add orderId, is_global to Notification, fix content type, add is_read to user_notifications

Revision ID: ver12
Revises: ver11
Create Date: 2026-01-10 13:13:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = 'ver12'
down_revision: Union[str, None] = 'ver11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    
    # Check notifications table columns
    notification_columns = [col['name'] for col in inspector.get_columns('notifications')]
    
    # Add order_id column to notifications if not exists
    if 'order_id' not in notification_columns:
        op.add_column(
            'notifications',
            sa.Column('order_id', sa.String(length=100), nullable=True)
        )
    
    # Add is_global column to notifications if not exists
    if 'is_global' not in notification_columns:
        op.add_column(
            'notifications',
            sa.Column('is_global', sa.Integer(), nullable=True)
        )
    
    # Fix content column type from Boolean/Integer to Text
    # Always run this as it's an alter, not add
    op.alter_column(
        'notifications',
        'content',
        existing_type=sa.Boolean(),
        type_=sa.Text(),
        existing_nullable=True
    )
    
    # Check user_notifications table columns
    user_notification_columns = [col['name'] for col in inspector.get_columns('user_notifications')]
    
    # Add is_read column to user_notifications if not exists
    if 'is_read' not in user_notification_columns:
        op.add_column(
            'user_notifications',
            sa.Column('is_read', sa.Boolean(), nullable=True, default=False)
        )
    
    # Add read_at column to user_notifications if not exists
    if 'read_at' not in user_notification_columns:
        op.add_column(
            'user_notifications',
            sa.Column('read_at', sa.DateTime(), nullable=True)
        )

def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    
    # Check user_notifications columns
    user_notification_columns = [col['name'] for col in inspector.get_columns('user_notifications')]
    
    if 'read_at' in user_notification_columns:
        op.drop_column('user_notifications', 'read_at')
    
    if 'is_read' in user_notification_columns:
        op.drop_column('user_notifications', 'is_read')
    
    # Alter content column back
    op.alter_column(
        'notifications',
        'content',
        existing_type=sa.Text(),
        type_=sa.Boolean(),
        existing_nullable=True
    )
    
    # Check notifications columns
    notification_columns = [col['name'] for col in inspector.get_columns('notifications')]
    
    if 'is_global' in notification_columns:
        op.drop_column('notifications', 'is_global')
    
    if 'order_id' in notification_columns:
        op.drop_column('notifications', 'order_id')
