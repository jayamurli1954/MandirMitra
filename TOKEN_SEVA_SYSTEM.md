# Token Seva System - Implementation Guide

## Overview

The Token Seva System handles small-value seva items (typically < ₹50) that use pre-printed serialized tokens instead of individual receipts. This cost-effective approach saves printing costs while maintaining proper accounting and audit controls.

## Key Features

### 1. **Token-Based Sevas**
- Sevas can be marked as "token seva" in the seva catalog
- Configurable threshold (default ₹50, can be set per temple)
- Color-coded tokens per seva type for easy identification
- Pre-printed serial numbers for control

### 2. **Token Inventory Management**
- Track pre-printed tokens with serial numbers
- Batch management (batch numbers, print dates)
- Status tracking: Available, Sold, Used, Lost, Damaged, Expired
- Prevent duplicate serial numbers

### 3. **Token Sales Recording**
- Quick token sale entry at counter
- Support for Cash and UPI payments
- Optional devotee information (can be anonymous)
- Counter-wise tracking
- Automatic accounting integration

### 4. **Daily Reconciliation**
- Automatic daily reconciliation reports
- Counter-wise summary
- Seva-wise summary
- Payment mode breakdown (Cash vs UPI)
- Discrepancy tracking
- Approval workflow

### 5. **Audit & Control Measures**

#### Serial Number Control
- Unique serial numbers prevent duplicates
- Status tracking prevents reuse
- Full audit trail of token lifecycle

#### Counter Control
- Counter-wise tracking
- Staff-wise tracking (who sold)
- Time-stamped sales

#### Financial Control
- Automatic posting to accounting
- Daily reconciliation required
- Approval workflow for reconciliation
- Discrepancy notes for exceptions

#### Inventory Control
- Real-time inventory status
- Batch tracking
- Expiry date support (optional)

## Database Schema

### Tables Created

1. **token_inventory** - Pre-printed token stock
2. **token_sales** - Token sale transactions
3. **token_reconciliations** - Daily reconciliation records

### Seva Model Updates

Added fields to `sevas` table:
- `is_token_seva` (Boolean) - Mark seva as token-based
- `token_color` (String) - Color code for tokens
- `token_threshold` (Float) - Amount threshold

### Temple Model Updates

Added field to `temples` table:
- `token_seva_threshold` (Float) - Default threshold (default ₹50)

## API Endpoints

### Token Inventory
- `POST /api/v1/token-seva/inventory/add` - Add tokens to inventory
- `GET /api/v1/token-seva/inventory/status` - Get inventory status by seva

### Token Sales
- `POST /api/v1/token-seva/sale` - Record a token sale
- `GET /api/v1/token-seva/sales` - Get sales with filters

### Reconciliation
- `POST /api/v1/token-seva/reconcile` - Create daily reconciliation
- `GET /api/v1/token-seva/reconcile/{date}` - Get reconciliation for date
- `PUT /api/v1/token-seva/reconcile/{id}/approve` - Approve reconciliation

## Workflow

### 1. Setup Phase

**Step 1: Configure Seva as Token Seva**
- Go to Seva Management
- Edit seva
- Enable "Is Token Seva"
- Set token color (e.g., "RED", "BLUE", "GREEN")
- Save

**Step 2: Add Token Inventory**
- Go to Token Seva → Inventory
- Select seva
- Enter batch details:
  - Serial number range (e.g., TK001-TK1000)
  - Token color
  - Batch number
  - Print date
- Bulk import or manual entry

### 2. Daily Operations

**Step 1: Record Token Sale**
- Counter staff selects seva
- System shows available tokens
- Staff enters:
  - Token serial number (from pre-printed token)
  - Payment mode (Cash/UPI)
  - UPI reference (if UPI)
  - Counter number
  - Optional: Devotee info
- System:
  - Validates token is available
  - Marks token as SOLD
  - Creates sale record
  - Posts to accounting (if configured)

**Step 2: End of Day Reconciliation**
- Admin/Manager runs daily reconciliation
- System generates:
  - Total tokens sold
  - Total amount (Cash + UPI breakdown)
  - Counter-wise summary
  - Seva-wise summary
  - Inventory status
- Manager reviews and approves
- Discrepancies can be noted

## Accounting Integration

Token sales are automatically posted to accounting:

**Debit:** Cash Account (if Cash) or Bank Account (if UPI)
**Credit:** Seva Revenue Account (from seva.account_id)

Journal Entry Format:
```
Date: [Sale Date]
Type: Receipt
Reference: TOKEN-[Serial Number]
Narration: Token sale - [Seva Name]

Dr. Cash/Bank        ₹[Amount]
Cr. Seva Revenue     ₹[Amount]
```

## Control Measures

### 1. Serial Number Control
- ✅ Unique serial numbers enforced
- ✅ Status prevents reuse
- ✅ Full audit trail

### 2. Counter Control
- ✅ Counter-wise tracking
- ✅ Staff-wise tracking
- ✅ Time-stamped transactions

### 3. Financial Control
- ✅ Automatic accounting
- ✅ Daily reconciliation
- ✅ Approval workflow
- ✅ Discrepancy tracking

### 4. Inventory Control
- ✅ Real-time status
- ✅ Batch tracking
- ✅ Expiry support

## Reports Available

1. **Daily Token Sales Report**
   - Date range filter
   - Seva filter
   - Counter filter
   - Payment mode filter

2. **Token Inventory Status**
   - By seva
   - Status breakdown
   - Available count

3. **Daily Reconciliation Report**
   - Total sales
   - Counter-wise breakdown
   - Seva-wise breakdown
   - Payment mode breakdown

## Best Practices

1. **Token Printing**
   - Use sequential serial numbers
   - Include batch numbers
   - Color code by seva type
   - Print expiry date (if applicable)

2. **Daily Operations**
   - Record sales immediately
   - Verify token serial numbers
   - Keep counter-wise records
   - Reconcile daily

3. **Reconciliation**
   - Run reconciliation at end of day
   - Verify physical tokens match system
   - Note any discrepancies
   - Get manager approval

4. **Audit**
   - Regular inventory audits
   - Verify serial number sequence
   - Check for missing tokens
   - Review reconciliation approvals

## Configuration

### Temple-Level Settings
- `token_seva_threshold`: Default threshold (default ₹50)

### Seva-Level Settings
- `is_token_seva`: Enable token seva
- `token_color`: Color code
- `token_threshold`: Override temple threshold (optional)

## Security & Permissions

Recommended permissions:
- **Counter Staff**: Record token sales
- **Manager**: View reports, create reconciliation
- **Admin**: Approve reconciliation, manage inventory

## Future Enhancements

1. Barcode/QR code scanning for tokens
2. Mobile app for token recording
3. Real-time inventory dashboard
4. Automated reconciliation alerts
5. Token expiry management
6. Bulk token import from Excel

## Migration Notes

After deploying this system:

1. Run database migration to create new tables
2. Update existing sevas to mark token sevas
3. Import existing token inventory (if any)
4. Configure accounting accounts for token sevas
5. Train staff on token recording process

## Support

For issues or questions:
- Check API documentation at `/docs`
- Review audit logs for transaction history
- Contact system administrator






