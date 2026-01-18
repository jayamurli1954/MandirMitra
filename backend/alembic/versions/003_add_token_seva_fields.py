"""add token seva fields

Revision ID: 003
Revises: 002
Create Date: 2025-11-26 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    # Add token seva fields to sevas table (only if they don't exist)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    sevas_columns = [col["name"] for col in inspector.get_columns("sevas")]
    temples_columns = [col["name"] for col in inspector.get_columns("temples")]

    if "is_token_seva" not in sevas_columns:
        op.add_column(
            "sevas", sa.Column("is_token_seva", sa.Boolean(), nullable=True, server_default="false")
        )
    if "token_color" not in sevas_columns:
        op.add_column("sevas", sa.Column("token_color", sa.String(length=50), nullable=True))
    if "token_threshold" not in sevas_columns:
        op.add_column("sevas", sa.Column("token_threshold", sa.Float(), nullable=True))

    # Add token_seva_threshold to temples table (only if it doesn't exist)
    if "token_seva_threshold" not in temples_columns:
        op.add_column(
            "temples",
            sa.Column("token_seva_threshold", sa.Float(), nullable=True, server_default="50.0"),
        )


def downgrade():
    # Remove token seva fields from sevas table
    op.drop_column("sevas", "token_threshold")
    op.drop_column("sevas", "token_color")
    op.drop_column("sevas", "is_token_seva")

    # Remove token_seva_threshold from temples table
    op.drop_column("temples", "token_seva_threshold")
