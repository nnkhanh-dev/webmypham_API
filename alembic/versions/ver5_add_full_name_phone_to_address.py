"""add full_name and phone_number to address

Revision ID: ver5
Revises: ver4
Create Date: 2025-12-30 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'ver5'
down_revision: Union[str, None] = 'ver4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        'addresses',
        sa.Column('full_name', sa.String(length=100), nullable=True)
    )
    op.add_column(
        'addresses',
        sa.Column('phone_number', sa.String(length=20), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('addresses', 'phone_number')
    op.drop_column('addresses', 'full_name')

