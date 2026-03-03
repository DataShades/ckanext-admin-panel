"""Add ap_support_ticket_message table.

Revision ID: e4b6d8f7a9c1
Revises: f5a5c7e5f284
Create Date: 2026-01-26 15:50:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e4b6d8f7a9c1"
down_revision = "f5a5c7e5f284"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ap_support_ticket_message",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "ticket_id",
            sa.Integer,
            sa.ForeignKey("ap_support_ticket.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "author_id", sa.UnicodeText, sa.ForeignKey("user.id"), nullable=False
        ),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=True,
        ),
    )


def downgrade():
    op.drop_table("ap_support_ticket_message")
