"""add_is_read_to_conversations

Revision ID: ver14
Revises: ver13
Create Date: 2026-01-10 20:56:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "ver15"
down_revision = "ver14"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add column is_read (Boolean = TINYINT(1) in MySQL)
    op.add_column(
        "conversations",
        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),  # ✅ MySQL-safe default
        ),
    )

    # 2. Create index for is_read
    op.create_index("ix_conversations_is_read", "conversations", ["is_read"])


def downgrade() -> None:
    # Drop index first
    op.drop_index("ix_conversations_is_read", table_name="conversations")

    # Drop column
    op.drop_column("conversations", "is_read")
