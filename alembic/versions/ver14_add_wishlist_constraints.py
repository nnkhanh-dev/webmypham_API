"""add_wishlist_constraints

Revision ID: ver14
Revises: ver13
Create Date: 2026-01-10 20:56:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ver14'
down_revision: Union[str, None] = 'ver13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique constraints, NOT NULL constraints, and indexes to wishlist tables"""
    
    # Add unique constraint for wishlists: one wishlist per user (respecting soft delete)
    op.create_unique_constraint(
        'uq_user_wishlist', 
        'wishlists', 
        ['user_id', 'deleted_at']
    )
    
    # Add unique constraint for wishlist_items: no duplicate products in wishlist (respecting soft delete)
    op.create_unique_constraint(
        'uq_wishlist_product', 
        'wishlist_items', 
        ['wishlist_id', 'product_type_id', 'deleted_at']
    )
    
    # Add NOT NULL constraints for foreign keys
    # Note: This will fail if there are NULL values in the database
    # Run check_wishlist_duplicates.py first to ensure data integrity
    op.alter_column('wishlists', 'user_id', 
                    existing_type=sa.String(36),
                    nullable=False)
    
    op.alter_column('wishlist_items', 'wishlist_id',
                    existing_type=sa.String(36), 
                    nullable=False)
    
    op.alter_column('wishlist_items', 'product_type_id',
                    existing_type=sa.String(36),
                    nullable=False)
    
    # Add indexes for better query performance
    op.create_index('ix_wishlists_user_id', 'wishlists', ['user_id'])
    op.create_index('ix_wishlists_deleted_at', 'wishlists', ['deleted_at'])
    op.create_index('ix_wishlist_items_wishlist_id', 'wishlist_items', ['wishlist_id'])
    op.create_index('ix_wishlist_items_product_type_id', 'wishlist_items', ['product_type_id'])
    op.create_index('ix_wishlist_items_deleted_at', 'wishlist_items', ['deleted_at'])


def downgrade() -> None:
    """Remove constraints and indexes"""
    
    # Drop indexes
    op.drop_index('ix_wishlist_items_deleted_at', 'wishlist_items')
    op.drop_index('ix_wishlist_items_product_type_id', 'wishlist_items')
    op.drop_index('ix_wishlist_items_wishlist_id', 'wishlist_items')
    op.drop_index('ix_wishlists_deleted_at', 'wishlists')
    op.drop_index('ix_wishlists_user_id', 'wishlists')
    
    # Remove NOT NULL constraints
    op.alter_column('wishlist_items', 'product_type_id',
                    existing_type=sa.String(36),
                    nullable=True)
    
    op.alter_column('wishlist_items', 'wishlist_id',
                    existing_type=sa.String(36),
                    nullable=True)
    
    op.alter_column('wishlists', 'user_id',
                    existing_type=sa.String(36),
                    nullable=True)
    
    # Drop unique constraints
    op.drop_constraint('uq_wishlist_product', 'wishlist_items', type_='unique')
    op.drop_constraint('uq_user_wishlist', 'wishlists', type_='unique')
