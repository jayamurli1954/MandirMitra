"""Add PAN and TAN numbers to temples table

Revision ID: 002
Revises: 001
Create Date: 2025-01-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def table_exists(table_name):
    """Check if a table exists in the database"""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def add_column_if_not_exists(table_name, column):
    """Add column only if the table exists and the column doesn't"""
    if not table_exists(table_name):
        return  # Fresh DB: ORM create_all already created table with all columns
    if not column_exists(table_name, column.name):
        op.add_column(table_name, column)


def upgrade() -> None:
    # Add PAN and TAN numbers
    add_column_if_not_exists(
        "temples", sa.Column("pan_number", sa.String(length=20), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("tan_number", sa.String(length=20), nullable=True)
    )


def downgrade() -> None:
    # Remove PAN and TAN numbers
    op.drop_column("temples", "tan_number")
    op.drop_column("temples", "pan_number")
