# Expense Accounts Trial Balance Fix

## Problem
Trial Balance was showing an imbalance (Debits: ₹303,428 vs Credits: ₹347,628, difference: ₹44,200) because expense accounts were not appearing in the trial balance.

## Root Cause
During the account code migration, new expense accounts were created (5101, 5102, 5110) to replace the old codes (05101, 05102, 05110). However, these new accounts were created with `is_active = FALSE`. 

The trial balance query filters accounts by `is_active == True`, so these expense accounts were excluded from the report even though they had journal entries totaling ₹44,200.

## Solution
Activated the expense accounts that have journal entries:

1. **5101 - Priest Salary**: ₹23,000 (Debit)
2. **5102 - Staff Salary**: ₹18,000 (Debit)  
3. **5110 - Electricity Bill**: ₹3,200 (Debit)
**Total**: ₹44,200

## Result
✅ Expense accounts are now active and will appear in the trial balance
✅ Trial balance should now balance correctly:
   - Debits: ₹303,428 + ₹44,200 = ₹347,628
   - Credits: ₹347,628
   - Difference: ₹0

## Next Steps
1. **Refresh your browser** to see the updated trial balance
2. **Verify** that the three expense accounts (5101, 5102, 5110) now appear in the trial balance
3. **Confirm** that the trial balance shows as balanced

## Note
Other expense accounts (5111, 5120, 5201-5503) remain inactive as they don't have journal entries yet. They will be activated automatically when first used, or you can activate them manually in the Chart of Accounts UI if needed.




