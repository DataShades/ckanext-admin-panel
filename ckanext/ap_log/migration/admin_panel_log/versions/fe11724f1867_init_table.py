"""Init table

Revision ID: fe11724f1867
Revises:
Create Date: 2024-03-11 13:20:05.331015

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fe11724f1867"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ap_logs",
        sa.Column("id", sa.Text, primary_key=True, unique=True),
        sa.Column("name", sa.Text),
        sa.Column("path", sa.Text),
        sa.Column("level", sa.Integer),
        sa.Column(
            "timestamp",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column("message", sa.Text),
        sa.Column("message_formatted", sa.Text),
    )


def downgrade():
    op.drop_table("ap_logs")
