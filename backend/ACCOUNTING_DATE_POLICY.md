# Accounting Entry Date Policy

## Critical Rule: All Collections Use Receipt Date

**ALL collections (donations, seva bookings, any income) MUST use the RECEIPT DATE for accounting entry date.**

This is critical for cash/bank reconciliation and prevents manipulation.

## Rule Details

### 1. Receipt Date Definition
- **Receipt Date** = Date when money was actually received
- This is a **system-generated date** that cannot be changed by users
- For donations: `donation_date` (defaults to current date)
- For seva bookings: `booking.created_at.date()` (system timestamp)

### 2. Accounting Entry Date
- Journal entry `entry_date` MUST always be the **receipt date**
- This ensures cash/bank account balances match actual cash/bank records
- Prevents backdating or forward-dating of entries for manipulation

### 3. Donations
- Donations are always **current date only** (no advance booking)
- `donation_date` = receipt date = accounting entry date
- No issue here since donation_date is always current date

### 4. Seva Bookings
- Seva bookings can have **advance booking** (future booking dates)
- **Receipt Date** = `booking.created_at.date()` (when money was received)
- **Booking Date** = `booking.booking_date` (when seva will be performed)
- **Accounting Entry Date** = Receipt Date (NOT booking date)

#### Example:
- Receipt Date: 2025-12-18 (money received today)
- Booking Date: 2025-12-22 (seva will be performed in future)
- Accounting Entry Date: **2025-12-18** (uses receipt date)
- Account: Credit to "Advance Seva Booking" (21003) - liability until seva date

### 5. Transfer Entries (Advance Booking to Income)
- When advance booking is transferred to income on seva date:
- **Transfer Entry Date** = Booking Date (seva date)
- This is the ONLY exception where we use booking date
- Reason: Transfer happens on the seva date when service is actually performed

## Implementation

### Donations (`backend/app/api/donations.py`)
```python
# Entry date should be receipt date (when money was received)
receipt_date = donation.donation_date  # donation_date IS the receipt date
entry_date = datetime.combine(receipt_date, datetime.min.time())
```

### Seva Bookings (`backend/app/api/sevas.py`)
```python
# Entry date should be receipt date (when money was received), not booking date
receipt_date = booking.created_at.date()  # System-generated receipt date
entry_date = datetime.combine(receipt_date, datetime.min.time())
```

### Transfer Entries (`backend/app/api/sevas.py`)
```python
# For transfer entries, entry_date should be booking_date (the seva date when transfer happens)
entry_date = datetime.combine(booking.booking_date, datetime.min.time())
```

## Why This Matters

1. **Cash/Bank Reconciliation**: Using receipt date ensures accounting entries match actual cash/bank movements
2. **Prevents Manipulation**: Cannot backdate or forward-date entries to manipulate financial records
3. **Audit Trail**: Clear distinction between when money was received vs when service is performed
4. **Regulatory Compliance**: Ensures accurate financial reporting and compliance with accounting standards

## Testing

Always verify:
- Donation entry date = donation_date (receipt date)
- Seva booking entry date = booking.created_at.date() (receipt date)
- Transfer entry date = booking.booking_date (seva date - exception)
- Trial Balance matches cash/bank account balances for the same date

















