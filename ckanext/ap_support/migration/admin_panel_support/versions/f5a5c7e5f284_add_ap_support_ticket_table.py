"""Add ap_support_ticket table

Revision ID: f5a5c7e5f284
Revises:
Create Date: 2024-01-23 15:31:38.784236

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f5a5c7e5f284"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ap_support_ticket",
        sa.Column("id", sa.Integer, primary_key=True, unique=True),
        sa.Column("subject", sa.Text),
        sa.Column("status", sa.Text),
        sa.Column("text", sa.Text),
        sa.Column("category", sa.Text),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "author_id",
            sa.UnicodeText,
            sa.ForeignKey("user.id"),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_table("ap_support_ticket")
