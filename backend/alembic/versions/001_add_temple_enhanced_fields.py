"""Add enhanced fields to temples table

Revision ID: 001
Revises:
Create Date: 2025-01-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def add_column_if_not_exists(table_name, column):
    """Add column only if it doesn't exist"""
    if not column_exists(table_name, column.name):
        op.add_column(table_name, column)


def upgrade() -> None:
    # Add multi-language support
    add_column_if_not_exists(
        "temples", sa.Column("name_kannada", sa.String(length=200), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("name_sanskrit", sa.String(length=200), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("deity_name_kannada", sa.String(length=200), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("deity_name_sanskrit", sa.String(length=200), nullable=True)
    )

    # Add banking information
    add_column_if_not_exists(
        "temples", sa.Column("bank_name", sa.String(length=200), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("bank_account_number", sa.String(length=50), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("bank_ifsc_code", sa.String(length=20), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("bank_branch", sa.String(length=200), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("bank_account_type", sa.String(length=50), nullable=True)
    )
    add_column_if_not_exists("temples", sa.Column("upi_id", sa.String(length=100), nullable=True))

    # Second bank account
    add_column_if_not_exists(
        "temples", sa.Column("bank_name_2", sa.String(length=200), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("bank_account_number_2", sa.String(length=50), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("bank_ifsc_code_2", sa.String(length=20), nullable=True)
    )

    # Add tax exemption certificates
    add_column_if_not_exists(
        "temples", sa.Column("certificate_80g_number", sa.String(length=100), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("certificate_80g_valid_from", sa.String(), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("certificate_80g_valid_to", sa.String(), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("certificate_12a_number", sa.String(length=100), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("certificate_12a_valid_from", sa.String(), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("fcra_registration_number", sa.String(length=100), nullable=True)
    )
    add_column_if_not_exists("temples", sa.Column("fcra_valid_from", sa.String(), nullable=True))
    add_column_if_not_exists("temples", sa.Column("fcra_valid_to", sa.String(), nullable=True))

    # Add financial configuration
    add_column_if_not_exists(
        "temples",
        sa.Column("financial_year_start_month", sa.Integer(), nullable=True, server_default="4"),
    )
    add_column_if_not_exists(
        "temples",
        sa.Column(
            "receipt_prefix_donation", sa.String(length=20), nullable=True, server_default="DON"
        ),
    )
    add_column_if_not_exists(
        "temples",
        sa.Column(
            "receipt_prefix_seva", sa.String(length=20), nullable=True, server_default="SEVA"
        ),
    )
    add_column_if_not_exists(
        "temples",
        sa.Column(
            "receipt_prefix_sponsorship", sa.String(length=20), nullable=True, server_default="SP"
        ),
    )
    add_column_if_not_exists(
        "temples",
        sa.Column(
            "receipt_prefix_inkind", sa.String(length=20), nullable=True, server_default="INK"
        ),
    )

    # Add authorized signatory details
    add_column_if_not_exists(
        "temples", sa.Column("chairman_name", sa.String(length=200), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("chairman_phone", sa.String(length=20), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("chairman_email", sa.String(length=100), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("authorized_signatory_name", sa.String(length=200), nullable=True)
    )
    add_column_if_not_exists(
        "temples",
        sa.Column("authorized_signatory_designation", sa.String(length=100), nullable=True),
    )
    add_column_if_not_exists(
        "temples", sa.Column("signature_image_url", sa.String(length=500), nullable=True)
    )

    # Add opening/closing times
    add_column_if_not_exists(
        "temples", sa.Column("opening_time", sa.String(length=10), nullable=True)
    )
    add_column_if_not_exists(
        "temples", sa.Column("closing_time", sa.String(length=10), nullable=True)
    )


def downgrade() -> None:
    # Remove all added columns
    op.drop_column("temples", "closing_time")
    op.drop_column("temples", "opening_time")
    op.drop_column("temples", "signature_image_url")
    op.drop_column("temples", "authorized_signatory_designation")
    op.drop_column("temples", "authorized_signatory_name")
    op.drop_column("temples", "chairman_email")
    op.drop_column("temples", "chairman_phone")
    op.drop_column("temples", "chairman_name")
    op.drop_column("temples", "receipt_prefix_inkind")
    op.drop_column("temples", "receipt_prefix_sponsorship")
    op.drop_column("temples", "receipt_prefix_seva")
    op.drop_column("temples", "receipt_prefix_donation")
    op.drop_column("temples", "financial_year_start_month")
    op.drop_column("temples", "fcra_valid_to")
    op.drop_column("temples", "fcra_valid_from")
    op.drop_column("temples", "fcra_registration_number")
    op.drop_column("temples", "certificate_12a_valid_from")
    op.drop_column("temples", "certificate_12a_number")
    op.drop_column("temples", "certificate_80g_valid_to")
    op.drop_column("temples", "certificate_80g_valid_from")
    op.drop_column("temples", "certificate_80g_number")
    op.drop_column("temples", "bank_ifsc_code_2")
    op.drop_column("temples", "bank_account_number_2")
    op.drop_column("temples", "bank_name_2")
    op.drop_column("temples", "upi_id")
    op.drop_column("temples", "bank_account_type")
    op.drop_column("temples", "bank_branch")
    op.drop_column("temples", "bank_ifsc_code")
    op.drop_column("temples", "bank_account_number")
    op.drop_column("temples", "bank_name")
    op.drop_column("temples", "deity_name_sanskrit")
    op.drop_column("temples", "deity_name_kannada")
    op.drop_column("temples", "name_sanskrit")
    op.drop_column("temples", "name_kannada")
