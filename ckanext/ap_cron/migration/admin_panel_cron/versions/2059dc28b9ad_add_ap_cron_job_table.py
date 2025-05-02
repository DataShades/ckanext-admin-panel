"""Add ap_cron_job table

Revision ID: 2059dc28b9ad
Revises:
Create Date: 2023-11-27 15:36:02.902203

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "2059dc28b9ad"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ap_cron_job",
        sa.Column("id", sa.Text, primary_key=True, unique=True),
        sa.Column("name", sa.Text),
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
        sa.Column("last_run", sa.DateTime, nullable=True),
        sa.Column("schedule", sa.Text),
        sa.Column("actions", sa.Text),
        sa.Column("data", JSONB, nullable=False),
        sa.Column("state", sa.Text),
        sa.Column("timeout", sa.Integer),
    )


def downgrade():
    op.drop_table("ap_cron_job")
