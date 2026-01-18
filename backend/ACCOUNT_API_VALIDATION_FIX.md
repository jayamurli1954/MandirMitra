# Account API Validation Fix

## Issue
The `/api/v1/accounts/` and `/api/v1/accounts/hierarchy` endpoints were failing with `ResponseValidationError` because the database was returning `None` values for boolean and float fields (`is_active`, `allow_manual_entry`, `is_system_account`, `opening_balance_debit`, `opening_balance_credit`), but the Pydantic response models expected non-nullable values.

## Root Cause
The database model (`Account`) defines these fields with default values, but existing rows may have `NULL` values in these columns. When Pydantic tries to validate the response, it fails because:
- `is_active: bool` expects a boolean, but gets `None`
- `is_system_account: bool` expects a boolean, but gets `None`
- `allow_manual_entry: bool` expects a boolean, but gets `None`
- `opening_balance_debit: float` expects a float, but gets `None`
- `opening_balance_credit: float` expects a float, but gets `None`

## Solution

### 1. Added Field Validators to AccountResponse Schema
Added `@field_validator` decorators for each field that might be `None` to convert `None` values to appropriate defaults:

```python
@field_validator('is_active', mode='before')
@classmethod
def validate_is_active(cls, v):
    """Handle None values for is_active"""
    return v if v is not None else True

@field_validator('allow_manual_entry', mode='before')
@classmethod
def validate_allow_manual_entry(cls, v):
    """Handle None values for allow_manual_entry"""
    return v if v is not None else True

@field_validator('is_system_account', mode='before')
@classmethod
def validate_is_system_account(cls, v):
    """Handle None values for is_system_account"""
    return v if v is not None else False

@field_validator('opening_balance_debit', mode='before')
@classmethod
def validate_opening_balance_debit(cls, v):
    """Handle None values for opening_balance_debit"""
    return v if v is not None else 0.0

@field_validator('opening_balance_credit', mode='before')
@classmethod
def validate_opening_balance_credit(cls, v):
    """Handle None values for opening_balance_credit"""
    return v if v is not None else 0.0
```

### 2. Updated build_account_hierarchy Function
Updated the `build_account_hierarchy` function in `backend/app/api/accounts.py` to handle `None` values when constructing dictionaries:

```python
"is_active": account.is_active if account.is_active is not None else True,
"is_system_account": account.is_system_account if account.is_system_account is not None else False,
"allow_manual_entry": account.allow_manual_entry if account.allow_manual_entry is not None else True,
"opening_balance_debit": account.opening_balance_debit if account.opening_balance_debit is not None else 0.0,
"opening_balance_credit": account.opening_balance_credit if account.opening_balance_credit is not None else 0.0,
```

## Files Modified
1. `backend/app/schemas/accounting.py` - Added field validators to `AccountResponse` class
2. `backend/app/api/accounts.py` - Updated `build_account_hierarchy` function to handle None values

## Impact
This fix ensures that:
- Chart of Accounts (COA) API endpoints work correctly
- Trial Balance API endpoints work correctly
- All accounting sub-modules that depend on the accounts API should now function properly

## Default Values Used
- `is_active`: `True`
- `allow_manual_entry`: `True`
- `is_system_account`: `False`
- `opening_balance_debit`: `0.0`
- `opening_balance_credit`: `0.0`

These defaults match the database model defaults and represent sensible defaults for accounts.




