"""add_description_to_types

Revision ID: v13
Revises: ver12
Create Date: 2026-01-10 17:08:17.871282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'v13'
down_revision: Union[str, None] = 'ver12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add description column to types table
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)
    
    columns = [col['name'] for col in inspector.get_columns('types')]
    
    if 'description' not in columns:
        op.add_column('types', sa.Column('description', sa.String(length=255), nullable=True))


def downgrade() -> None:
    # Remove description column from types table
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)
    
    columns = [col['name'] for col in inspector.get_columns('types')]
    
    if 'description' in columns:
        op.drop_column('types', 'description')
