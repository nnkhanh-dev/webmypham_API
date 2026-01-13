"""add email_verifications table

Revision ID: ver3
Revises: ver2
Create Date: 2026-01-13 21:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ver3'
down_revision: Union[str, None] = 'ver2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tạo bảng email_verifications
    op.create_table('email_verifications',
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('code_hash', sa.String(length=255), nullable=False),
    sa.Column('attempts', sa.Integer(), nullable=True, server_default='0'),
    sa.Column('resend_count', sa.Integer(), nullable=True, server_default='0'),
    sa.Column('last_sent_at', sa.DateTime(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('verified', sa.Boolean(), nullable=True, server_default='0'),
    sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(length=36), nullable=True),
    sa.Column('updated_by', sa.String(length=36), nullable=True),
    sa.Column('deleted_by', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Tạo các indexes để tối ưu query
    op.create_index(op.f('ix_email_verifications_user_id'), 'email_verifications', ['user_id'], unique=False)
    op.create_index(op.f('ix_email_verifications_is_active'), 'email_verifications', ['is_active'], unique=False)
    op.create_index(op.f('ix_email_verifications_expires_at'), 'email_verifications', ['expires_at'], unique=False)


def downgrade() -> None:
    # Xóa indexes
    op.drop_index(op.f('ix_email_verifications_expires_at'), table_name='email_verifications')
    op.drop_index(op.f('ix_email_verifications_is_active'), table_name='email_verifications')
    op.drop_index(op.f('ix_email_verifications_user_id'), table_name='email_verifications')
    
    # Xóa bảng
    op.drop_table('email_verifications')
