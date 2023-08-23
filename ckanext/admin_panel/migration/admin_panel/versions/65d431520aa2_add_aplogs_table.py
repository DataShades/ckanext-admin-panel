"""Add ApLogs table

Revision ID: 65d431520aa2
Revises:
Create Date: 2023-08-21 10:18:49.128929

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "65d431520aa2"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ap_logs",
        sa.Column("id", sa.Integer, primary_key=True, unique=True, autoincrement=True, index=True),
        sa.Column("name", sa.Text),
        sa.Column("path", sa.Text),
        sa.Column("level", sa.Integer),
        sa.Column(
            "timestamp",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.current_timestamp(),
            index=True
        ),
        sa.Column("message", sa.Text),
        sa.Column("message_formatted", sa.Text),
    )


def downgrade():
    op.drop_table("ap_logs")
