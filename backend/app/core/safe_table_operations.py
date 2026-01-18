"""
Safe Table Operations
Prevents SQL injection in backup/restore and other database operations
"""

from sqlalchemy import inspect, MetaData
from sqlalchemy.engine import Engine
from fastapi import HTTPException
from typing import Set, List
import logging

logger = logging.getLogger(__name__)


def get_safe_table_list(engine: Engine) -> Set[str]:
    """
    Get list of all valid table names from database metadata

    Args:
        engine: SQLAlchemy engine

    Returns:
        Set of valid table names
    """
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    logger.debug(f"Found {len(tables)} tables in database")
    return tables


def validate_table_name(engine: Engine, table_name: str) -> bool:
    """
    Validate that a table name exists in the database
    Prevents SQL injection by checking against actual database metadata

    Args:
        engine: SQLAlchemy engine
        table_name: Name of table to validate

    Returns:
        True if valid

    Raises:
        HTTPException: If table name is invalid
    """
    valid_tables = get_safe_table_list(engine)

    if table_name not in valid_tables:
        logger.warning(f"Invalid table name attempted: {table_name}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid table name: {table_name}. Table does not exist."
        )

    logger.debug(f"Validated table name: {table_name}")
    return True


def get_table_columns(engine: Engine, table_name: str) -> List[str]:
    """
    Get list of column names for a table (after validation)

    Args:
        engine: SQLAlchemy engine
        table_name: Name of table

    Returns:
        List of column names
    """
    # Validate first
    validate_table_name(engine, table_name)

    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]

    return columns


# Allowlist of tables that should be included in backups
# Add or remove tables based on your schema
BACKUP_ALLOWED_TABLES = {
    'temples',
    'users',
    'devotees',
    'donations',
    'donation_categories',
    'sevas',
    'seva_bookings',
    'seva_exchange_requests',
    'accounts',
    'journal_entries',
    'journal_lines',
    'assets',
    'asset_categories',
    'asset_transfers',
    'asset_valuation_history',
    'asset_physical_verification',
    'asset_insurance',
    'asset_documents',
    'capital_work_in_progress',
    'inventory',
    'items',
    'stock_balances',
    'stock_movements',
    'stores',
    'purchase_orders',
    'purchase_order_items',
    'grn',
    'grn_items',
    'gin',
    'gin_items',
    'employees',
    'departments',
    'vendors',
    'bank_accounts',
    'bank_transactions',
    'bank_statements',
    'bank_statement_entries',
    'bank_reconciliations',
    'reconciliation_outstanding_items',
    'hundi_masters',
    'hundi_openings',
    'hundi_denomination_counts',
    'upi_payments',
    'inkind_donations',
    'inkind_consumptions',
    'sponsorships',
    'sponsorship_payments',
    'financial_years',
    'financial_periods',
    'period_closings',
    'budgets',
    'panchang_display_settings',
    'audit_logs',
}


def validate_backup_table(table_name: str) -> bool:
    """
    Validate table is allowed for backup operations

    Args:
        table_name: Name of table

    Returns:
        True if allowed

    Raises:
        HTTPException: If table is not in allowlist
    """
    if table_name not in BACKUP_ALLOWED_TABLES:
        logger.warning(f"Table not in backup allowlist: {table_name}")
        raise HTTPException(
            status_code=400,
            detail=f"Table '{table_name}' is not allowed for backup operations"
        )

    return True
