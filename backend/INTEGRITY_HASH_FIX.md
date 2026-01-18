# Integrity Hash Column Fix

## Problem
The `integrity_hash` column is defined in the JournalEntry model but doesn't exist in the database yet. This causes queries to fail with:
```
column journal_entries.integrity_hash does not exist
```

## Solution
Updated all JournalEntry queries that only need basic fields (id, entry_number, temple_id) to use `load_only()` to exclude the `integrity_hash` column.

## Files Modified
- `backend/app/api/sevas.py` - Fixed multiple JournalEntry queries
- `backend/app/api/donations.py` - Fixed JournalEntry query
- `backend/app/models/accounting.py` - Updated comment to note column may not exist

## Changes
All queries like:
```python
db.query(JournalEntry).filter(...).order_by(...).first()
```

Were changed to:
```python
from sqlalchemy.orm import load_only
db.query(JournalEntry).options(
    load_only(JournalEntry.id, JournalEntry.entry_number, JournalEntry.temple_id)
).filter(...).order_by(...).first()
```

## Note
This is a temporary fix. Once the integrity_hash migration is run, these queries can be reverted to normal queries. However, using `load_only()` is also a performance optimization since it only loads needed columns.




