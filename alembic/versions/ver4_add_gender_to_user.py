"""add gender column to user

Revision ID: ver4
Revises: ver3
Create Date: 2026-01-04 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'ver4'
down_revision: Union[str, None] = 'ver3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('gender', sa.SmallInteger(), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('users', 'gender')