# How to Fix BankReconciliation Import Error in CI/CD

## Problem
The CI/CD is failing with:
```
ImportError: cannot import name 'BankReconciliation' from 'app.models.upi_banking'
```

This happens because `BankReconciliation` was moved from `app.models.upi_banking` to `app.models.bank_reconciliation`, but some branches still have the old import.

## Solution Steps

### Step 1: Verify Local Fix is Correct ✅

The local file `backend/app/main.py` should have:

**Lines 41-46:**
```python
from app.models.bank_reconciliation import (
    BankStatement,
    BankStatementEntry,
    BankReconciliation,  # ✅ Correct location
    ReconciliationOutstandingItem,
)
```

**Line 57:**
```python
from app.models.upi_banking import UpiPayment, BankAccount, BankTransaction  # ✅ No BankReconciliation
```

**NOT this (old/wrong version):**
```python
from app.models.upi_banking import (
    UpiPayment, BankAccount, BankTransaction, BankReconciliation  # ❌ WRONG!
)
```

### Step 2: Commit and Push Fix to Main Branch

If you haven't already committed the fix:

```bash
# Make sure you're on main branch
git checkout main

# Check the current status
git status

# Add the fixed files
git add backend/app/main.py backend/alembic/env.py backend/seed_chart_of_accounts.py backend/requirements.txt

# Commit the fix
git commit -m "fix: Move BankReconciliation import from upi_banking to bank_reconciliation

- Fix ImportError: cannot import name 'BankReconciliation' from 'app.models.upi_banking'
- Update app/main.py to import BankReconciliation from app.models.bank_reconciliation
- Update alembic/env.py with correct imports
- Fix seed_chart_of_accounts.py imports
- Reorder email-validator in requirements.txt"

# Push to main
git push origin main
```

### Step 3: Update Feature Branches

For each feature branch that's failing CI/CD:

#### Option A: Rebase from Main (Recommended)

```bash
# Checkout your feature branch
git checkout your-feature-branch

# Fetch latest changes
git fetch origin

# Rebase from main
git rebase origin/main

# If there are conflicts in app/main.py, keep the version from main (the fixed one)
# The correct version should have:
# - BankReconciliation imported from bank_reconciliation (lines 41-46)
# - Single-line import from upi_banking without BankReconciliation (line 57)

# Push the updated branch (may need force push if already pushed)
git push origin your-feature-branch --force-with-lease
```

#### Option B: Merge Main into Feature Branch

```bash
# Checkout your feature branch
git checkout your-feature-branch

# Fetch latest changes
git fetch origin

# Merge main into your branch
git merge origin/main

# Resolve any conflicts in app/main.py by keeping the version from main

# Push the updated branch
git push origin your-feature-branch
```

#### Option C: Manually Fix the Branch

If rebasing/merging is not possible, manually fix `backend/app/main.py`:

1. **Find the wrong import** (around line 25-30, may vary):
   ```python
   from app.models.upi_banking import (
       UpiPayment, BankAccount, BankTransaction, BankReconciliation  # ❌
   )
   ```

2. **Replace with correct imports**:
   ```python
   # Around lines 41-46, ensure this exists:
   from app.models.bank_reconciliation import (
       BankStatement,
       BankStatementEntry,
       BankReconciliation,  # ✅
       ReconciliationOutstandingItem,
   )
   
   # Around line 57, ensure this exists (single line, no BankReconciliation):
   from app.models.upi_banking import UpiPayment, BankAccount, BankTransaction  # ✅
   ```

3. **Remove the old multi-line import** that includes `BankReconciliation`

4. **Commit and push**:
   ```bash
   git add backend/app/main.py
   git commit -m "fix: Update BankReconciliation import to use bank_reconciliation module"
   git push origin your-feature-branch
   ```

### Step 4: Verify Fix

After updating branches, verify the fix:

```bash
# Check that app/main.py has correct imports
grep -A 5 "from app.models.bank_reconciliation" backend/app/main.py
grep "from app.models.upi_banking" backend/app/main.py

# Should show:
# - BankReconciliation in bank_reconciliation import
# - No BankReconciliation in upi_banking import
```

### Step 5: Check All Files

Also verify these files are correct:

```bash
# Check alembic/env.py
grep -A 2 "from app.models.upi_banking" backend/alembic/env.py
# Should NOT include BankReconciliation

# Check seed_chart_of_accounts.py (if it exists)
grep -A 2 "from app.models.upi_banking" backend/seed_chart_of_accounts.py
# Should NOT include BankReconciliation
```

## Quick Reference: Correct Import Structure

### ✅ CORRECT (what should be in the file):

```python
# In app/main.py:

# Lines 41-46: Import BankReconciliation from correct module
from app.models.bank_reconciliation import (
    BankStatement,
    BankStatementEntry,
    BankReconciliation,  # ✅
    ReconciliationOutstandingItem,
)

# ... other imports ...

# Line 57: Import from upi_banking WITHOUT BankReconciliation
from app.models.upi_banking import UpiPayment, BankAccount, BankTransaction  # ✅
```

### ❌ WRONG (what causes the error):

```python
from app.models.upi_banking import (
    UpiPayment, BankAccount, BankTransaction, BankReconciliation  # ❌
)
```

## Prevention

To prevent this in the future:

1. **Always merge/rebase from main** before creating new branches
2. **Run tests locally** before pushing: `cd backend && pytest`
3. **Check imports** before committing changes to `app/main.py`

## Files That Were Fixed

1. ✅ `backend/app/main.py` - Main application file
2. ✅ `backend/alembic/env.py` - Alembic migrations
3. ✅ `backend/seed_chart_of_accounts.py` - Seed script
4. ✅ `backend/requirements.txt` - Dependencies (email-validator order)

All these files are now correct in the local repository. The fix just needs to be propagated to GitHub branches.
