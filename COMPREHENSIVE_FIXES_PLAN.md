# Comprehensive Fixes Plan

## Issues Identified

### 1. ✅ Trial Balance Showing Wrong Accounts
**Problem:** All donations are cash, but trial balance shows:
- 4101: Donation - Cash: ₹6,500 ✓
- 4102: Donation - Online/UPI: ₹5,500 ✗ (WRONG - should be 0)

**Root Cause:** Donations are being credited to payment-mode accounts (4102, 4103) instead of category-linked accounts (4101, 4111, 4112, etc.)

**Fix Applied:** 
- Modified `post_donation_to_accounting()` to prioritize category-linked accounts
- Removed fallback to payment-mode accounts (4102, 4103)
- Only uses 4101 as absolute last resort if category not linked

**Action Required:**
1. Link donation categories to accounts using: `python -m scripts.link_accounts_to_categories_sevas`
2. Re-run backfill for existing donations: `python -m scripts.backfill_donation_journal_entries`
3. Or manually update existing journal entries to use correct accounts

---

### 2. ⚠️ Seva Booking Not Creating Accounting Entry
**Problem:** "Sarva Seva" ₹2,000 booking successful but no journal entry

**Root Cause:** 
- Seva not linked to account (account_id is NULL)
- Default account 4208 might not exist
- Error handling might be swallowing the error

**Fix Applied:**
- Added better error logging in seva booking creation
- Will show warning if accounting entry fails

**Action Required:**
1. Link "Sarva Seva" to account (4203 or appropriate account)
2. Create default account 4208 if it doesn't exist
3. Re-run seva backfill: `python -m scripts.backfill_seva_journal_entries`

---

### 3. 📊 Dashboard Enhancements Needed

#### Current State:
- Shows: Today's donation, Cumulative for month, Cumulative for year, Total devotees

#### Required Changes:
**First Line:**
- Today's Donation
- Cumulative for Month
- Cumulative for Year
- (Remove: Total Devotees)

**Second Line:**
- Today's Seva
- Cumulative for Month
- Cumulative for Year

**Files to Modify:**
- `frontend/src/pages/Dashboard.js` (or similar)
- Backend API endpoint for dashboard stats

---

### 4. 📈 Category-Wise Donation Report

**Requirements:**
- Default: Show category-wise donations for today
- Option: Custom date range
- Group by donation category
- Show: Category name, count, total amount

**Implementation:**
- New API endpoint: `GET /api/v1/donations/report/category-wise`
- Frontend page: Category-wise Donation Report
- Date range picker (default: today)

---

### 5. 📋 Detailed Donation Report

**Requirements:**
- Date range selection
- Columns:
  - Date
  - Devotee Name
  - Mobile Number
  - Donation Category
  - Payment Mode
  - Amount
- Export to Excel/PDF
- Filter by category, payment mode, date range

**Implementation:**
- Enhance existing donation report endpoint
- Add new detailed report endpoint
- Frontend: Detailed Donation Report page with filters

---

### 6. 📋 Detailed Seva Report

**Requirements:**
- Similar to donation report
- Additional columns:
  - Seva Date
  - Status (Completed/Pending/Postponed)
  - Original Date (if postponed/preponed)
- Status Logic:
  - Current date or past = Completed
  - Future = Pending
- Postpone/Prepone functionality:
  - Edit seva date
  - Requires admin approval
  - Track original date and new date
  - Approval workflow

**Implementation:**
- New API endpoints:
  - `GET /api/v1/sevas/bookings/report/detailed`
  - `PUT /api/v1/sevas/bookings/{id}/reschedule` (with approval)
  - `POST /api/v1/sevas/bookings/{id}/approve-reschedule`
- Frontend: Detailed Seva Report page
- Approval workflow UI

---

### 7. 📅 3-Day Seva Schedule Report

**Requirements:**
- Show all sevas for next 3 days from current date
- Help temple authority make arrangements
- Columns:
  - Date
  - Time
  - Seva Name
  - Devotee Name
  - Mobile Number
  - Status
  - Special Requests

**Implementation:**
- API endpoint: `GET /api/v1/sevas/bookings/schedule?days=3`
- Frontend: 3-Day Schedule page
- Can be displayed on dashboard or separate page

---

### 8. 📱 SMS Reminder System

**Requirements:**
- Send SMS to devotees 7-10 days before seva date
- Configurable reminder days (settings)
- Track sent reminders
- Manual trigger option

**Implementation:**
- SMS service integration (Twilio/AWS SNS/Indian SMS gateway)
- Background job scheduler (Celery or similar)
- Database table for tracking reminders
- Settings page configuration

---

### 9. ⚙️ Settings Page Completion

**Requirements:**
- Password protected (main admin only)
- All system settings:
  - Temple information
  - Financial year
  - Receipt prefixes
  - SMS/Email settings
  - Reminder settings
  - Account linking
  - User management
- Password prompt before access

**Implementation:**
- Settings page with password protection
- Backend: Settings API with admin-only access
- Frontend: Settings page with password modal

---

## Priority Order

1. **P0 (Critical):**
   - ✅ Fix trial balance account mapping
   - ⚠️ Fix seva accounting entry creation
   - Link accounts to categories/sevas

2. **P1 (High):**
   - Dashboard enhancements
   - Category-wise donation report
   - Detailed donation/seva reports

3. **P2 (Medium):**
   - 3-day seva schedule
   - Postpone/prepone with approval

4. **P3 (Low):**
   - SMS reminder system
   - Settings page completion

---

## Next Steps

1. **Immediate:** Run linking script and re-backfill donations
2. **Short-term:** Implement dashboard and basic reports
3. **Medium-term:** Add seva management features
4. **Long-term:** SMS and advanced settings

---

**Last Updated:** November 2025







