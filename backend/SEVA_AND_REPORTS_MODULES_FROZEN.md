# Seva & Reports Modules - Frozen Documentation

## ⚠️ CRITICAL: DO NOT MODIFY WITHOUT TESTING

The Seva Module, Seva Management Module, and Seva & Donation Report Module have been stabilized and verified working. These modules are now **FROZEN** and should not be modified without thorough testing.

---

## Module 1: Seva Module (Seva Booking)

### Status: ✅ COMPLETE & VERIFIED
**Last Tested:** December 21, 2025  
**Status:** Working as expected

### Core Files (FROZEN):

#### Backend:
1. **`backend/app/models/seva.py`**
   - `Seva` model - Seva catalog definitions
   - `SevaBooking` model - Booking records
   - `SevaAvailability` enum - Daily, Specific Day, Except Day
   - `SevaBookingStatus` enum - Pending, Confirmed, Completed, Cancelled
   - `except_days` field - JSON string storing excluded days list

2. **`backend/app/schemas/seva.py`**
   - `SevaBase`, `SevaCreate`, `SevaUpdate`, `SevaResponse` - Seva schemas
   - `SevaBookingBase`, `SevaBookingCreate`, `SevaBookingResponse` - Booking schemas
   - `except_days` field validators for JSON string parsing
   - `field_validator` for `except_days` to parse JSON strings to lists

3. **`backend/app/api/sevas.py`**
   - `list_sevas()` - Get available sevas
   - `create_seva()` - Add new seva
   - `update_seva()` - Update existing seva (handles `except_days` JSON conversion)
   - `get_seva()` - Get single seva details
   - `delete_seva()` - Delete seva
   - `list_bookings()` - Get all bookings with filters
   - `create_booking()` - Create new seva booking
   - `get_booking()` - Get single booking details
   - `update_booking()` - Update booking
   - `cancel_booking()` - Cancel a booking
   - `request_reschedule()` - Request booking reschedule
   - `approve_reschedule()` - Approve/reject reschedule request
   - `get_pending_reschedule_requests()` - Get pending reschedule requests
   - `serialize_booking_response()` - Helper to serialize booking with relationships
   - `get_seva_safely()` - Safe seva query handling missing columns
   - `_generate_seva_receipt_pdf()` - Generate PDF receipt (shows Receipt Date vs Seva Date)

#### Frontend:
4. **`frontend/src/pages/SevaBooking.js`**
   - Seva booking form
   - Date and time selection
   - Devotee selection/creation
   - Payment collection
   - Booking confirmation

### Key Features Implemented:
- ✅ Seva catalog management
- ✅ Seva availability configuration (Daily, Specific Day, Except Day)
- ✅ Multi-day exclusion for sevas (`except_days` field)
- ✅ Seva booking creation with payment
- ✅ Booking status management
- ✅ Reschedule request workflow
- ✅ Reschedule approval workflow
- ✅ Booking cancellation
- ✅ Receipt generation with proper date distinction:
  - **Receipt Date**: Date when booking was made (`booking.created_at`)
  - **Seva Date**: Date when seva will be performed (`booking.booking_date`)
- ✅ Status determination logic:
  - Completed: `booking_date < today`
  - Pending: `booking_date >= today` (allows rescheduling)

### Database Schema:
- `sevas` table includes `except_days` column (TEXT, nullable) - stores JSON array of excluded day numbers
- `seva_bookings` table includes reschedule fields:
  - `original_booking_date`
  - `reschedule_requested_date`
  - `reschedule_reason`
  - `reschedule_approved`
  - `reschedule_approved_by`
  - `reschedule_approved_at`

---

## Module 2: Seva Management Module

### Status: ✅ COMPLETE & VERIFIED
**Last Tested:** December 21, 2025  
**Status:** Working as expected

### Core Files (FROZEN):

#### Backend:
1. **`backend/app/api/sevas.py`** (shared with Seva Module)
   - All seva CRUD operations
   - `except_days` handling for multi-day exclusion

#### Frontend:
2. **`frontend/src/pages/SevaManagement.js`**
   - Seva create/edit form
   - Multi-select checkboxes for `except_days` (excluded days)
   - Seva availability type selection (Daily, Specific Day, Except Day)
   - Seva pricing, description, category configuration
   - Form handles JSON string parsing/stringifying for `except_days`

3. **`frontend/src/pages/SevaSchedule.js`**
   - Three-day seva schedule view
   - Date column renamed to "Seva Date" for clarity
   - Booking status display
   - Priest assignment
   - Refund processing

4. **`frontend/src/pages/SevaRescheduleApproval.js`**
   - View pending reschedule requests
   - Approve/reject reschedule requests
   - Only accessible to admin/temple_manager roles

### Key Features Implemented:
- ✅ Seva catalog CRUD operations
- ✅ Seva availability configuration:
  - **Daily**: Available every day
  - **Specific Day**: Available only on one specific day (e.g., Monday)
  - **Except Day**: Available all days except specified days (e.g., except Monday and Saturday)
- ✅ Multi-select dropdown for excluded days in frontend
- ✅ JSON storage of `except_days` in database
- ✅ Seva schedule management
- ✅ Priest assignment to bookings
- ✅ Reschedule approval workflow

### Frontend UI Components:
- Multi-select checkboxes for day exclusion (Sunday=0, Monday=1, ..., Saturday=6)
- Dropdown placeholders properly display selected values
- No text overlapping issues in dropdowns

---

## Module 3: Seva & Donation Report Module

### Status: ✅ COMPLETE & VERIFIED
**Last Tested:** December 21, 2025  
**Status:** Working as expected

### Core Files (FROZEN):

#### Backend:
1. **`backend/app/api/reports.py`**
   - `get_detailed_seva_report()` - Detailed seva report with filters
     - Filters by receipt date range (not seva date)
     - Status filter: All, Completed, Pending
     - Seva type filter: All Sevas or specific seva
     - Status determination: Completed if `booking_date < today`, Pending if `booking_date >= today`
   - `export_detailed_seva_excel()` - Excel export
   - `export_detailed_seva_pdf()` - PDF export
   - `get_detailed_donation_report()` - Detailed donation report
   - `get_three_day_seva_schedule()` - Three-day schedule report

#### Frontend:
2. **`frontend/src/pages/DetailedSevaReport.js`**
   - Date range selection
   - Status filter: All Status, Completed, Pending
   - Seva Type filter: All Sevas or specific seva selection
   - Seva type-wise summary table
   - Detailed booking list with totals row
   - Export to Excel/PDF
   - Print functionality (sidebar and filters hidden)
   - Dropdown placeholders properly display selected values

3. **`frontend/src/pages/DetailedDonationReport.js`**
   - Date range selection
   - Category filter
   - Payment mode filter
   - Detailed donation list with totals row
   - Export to Excel/CSV
   - Print functionality (sidebar and filters hidden)

4. **`frontend/src/pages/CategoryWiseDonationReport.js`**
   - Category-wise donation summary
   - Export and print functionality

5. **`frontend/src/pages/SevaSchedule.js`** (Report view)
   - Three-day seva schedule
   - Export and print functionality

6. **`frontend/src/index.css`**
   - Print media queries:
     - Hides sidebar (Drawer)
     - Hides top navigation (AppBar)
     - Hides buttons and filter sections (`.no-print` class)
     - Optimizes table font size (10px) and padding for printing
     - Ensures all columns are visible in print
     - Proper table borders and spacing

### Key Features Implemented:
- ✅ Detailed Seva Report:
  - Filters by receipt date (when booking was created)
  - Status filter (All, Completed, Pending)
  - Seva type filter (All or specific seva)
  - Seva type-wise summary
  - Total row showing count, completed count, pending count, and total amount
  - Receipt Date vs Seva Date distinction in table
  
- ✅ Detailed Donation Report:
  - Date range filter
  - Category filter
  - Payment mode filter
  - Total row showing count and total amount

- ✅ Print Functionality:
  - Hides sidebar and navigation
  - Hides filter sections and buttons
  - Shows only report content
  - All columns visible in print
  - Totals row included

- ✅ Export Functionality:
  - Excel export (Detailed Seva Report)
  - PDF export (Detailed Seva Report)
  - CSV export (Donation Report)
  - Proper data formatting

### Report Logic:
- **Receipt Date**: Used for filtering report date range (when money was received/booking was created)
- **Seva Date / Booking Date**: Used for status determination (when seva will be/performed)
- **Status Logic**: 
  - Completed: `booking_date < today`
  - Pending: `booking_date >= today`
  - This allows bookings for today to be rescheduled

---

## Testing Checklist

Before modifying any files in these modules, verify:

### Seva Module:
- [ ] Seva catalog CRUD operations work
- [ ] Seva booking creation works
- [ ] `except_days` field saves and loads correctly (JSON format)
- [ ] Multi-day exclusion works (e.g., exclude Monday and Saturday)
- [ ] Reschedule request workflow works
- [ ] Reschedule approval workflow works
- [ ] Receipt shows correct Receipt Date and Seva Date
- [ ] Booking status determination is correct (today's bookings are Pending)

### Seva Management Module:
- [ ] Seva create/edit form works
- [ ] Multi-select checkboxes for excluded days work
- [ ] Dropdown placeholders display correctly (no overlapping text)
- [ ] Seva schedule displays correctly
- [ ] Priest assignment works
- [ ] Three-day schedule report works

### Report Module:
- [ ] Detailed Seva Report filters work (status, seva type, date range)
- [ ] Detailed Donation Report filters work (category, payment mode, date range)
- [ ] Status filter shows correct data:
  - "All Status" shows both completed and pending
  - "Completed" shows only past bookings
  - "Pending" shows today and future bookings
- [ ] Seva type filter works (All or specific seva)
- [ ] Totals row displays correctly
- [ ] Print functionality works (no sidebar, all columns visible)
- [ ] Export to Excel/PDF/CSV works
- [ ] All columns are visible in printed reports
- [ ] Receipt Date vs Seva Date columns are clearly labeled

---

## Known Issues & Solutions

1. **`except_days` Storage Format:**
   - Stored as JSON string in database (e.g., `"[1, 6]"` for Monday and Saturday)
   - Frontend sends as array, backend converts to JSON string
   - Backend response uses `field_validator` to parse JSON string back to array

2. **Status Determination:**
   - Current day bookings are considered "Pending" (not "Completed")
   - This allows rescheduling of bookings for today
   - Logic: `booking_date < today` = Completed, `booking_date >= today` = Pending

3. **Report Date Filtering:**
   - Reports filter by receipt date (`created_at`), not booking date
   - This ensures reports match accounting records (when money was received)

4. **Print Column Visibility:**
   - Reduced font size to 10px for better column fit
   - Reduced padding to 4px 6px
   - Set `white-space: nowrap` to prevent column wrapping
   - All columns should be visible in print

5. **Dropdown Placeholder Display:**
   - Use non-empty values ('all') instead of empty strings
   - Material-UI automatically handles label shrinking
   - No overlapping text issues

---

## API Endpoints

### Seva Endpoints:
```
GET    /api/v1/sevas/                        - List all sevas
POST   /api/v1/sevas/                        - Create new seva
GET    /api/v1/sevas/{id}                    - Get seva details
PUT    /api/v1/sevas/{id}                    - Update seva
DELETE /api/v1/sevas/{id}                    - Delete seva
GET    /api/v1/sevas/dropdown-options        - Get sevas for dropdown
```

### Seva Booking Endpoints:
```
GET    /api/v1/sevas/bookings/               - List bookings with filters
POST   /api/v1/sevas/bookings/               - Create booking
GET    /api/v1/sevas/bookings/{id}           - Get booking details
PUT    /api/v1/sevas/bookings/{id}           - Update booking
PUT    /api/v1/sevas/bookings/{id}/cancel    - Cancel booking
PUT    /api/v1/sevas/bookings/{id}/reschedule - Request reschedule
PUT    /api/v1/sevas/bookings/{id}/approve-reschedule - Approve reschedule
GET    /api/v1/sevas/bookings/pending-reschedule - Get pending requests
GET    /api/v1/sevas/bookings/{id}/receipt   - Get booking receipt PDF
```

### Report Endpoints:
```
GET    /api/v1/reports/sevas/detailed        - Detailed seva report
GET    /api/v1/reports/sevas/detailed/excel  - Excel export
GET    /api/v1/reports/sevas/detailed/pdf    - PDF export
GET    /api/v1/reports/donations/detailed    - Detailed donation report
GET    /api/v1/reports/sevas/schedule        - Three-day schedule
```

---

## Database Migration Notes

If the `except_days` column doesn't exist, run:
```bash
python backend/scripts/add_except_days_column.py
```

This script:
- Adds `except_days` column to `sevas` table (TEXT, nullable)
- Handles both SQLite and PostgreSQL
- Includes error handling and Unicode encoding fixes

---

## Last Verified

- **Date:** December 21, 2025
- **Status:** ✅ All modules working correctly
- **Tested By:** User verification completed
- **Key Functionality:**
  - ✅ Seva booking with payment
  - ✅ Seva management with multi-day exclusion
  - ✅ Reschedule request and approval workflow
  - ✅ Detailed reports with proper filtering
  - ✅ Print functionality with all columns visible
  - ✅ Export functionality (Excel, PDF, CSV)
  - ✅ Totals row in reports
  - ✅ Receipt date vs Seva date distinction

---

## Notes

1. **Do NOT modify** the status determination logic without understanding the business requirement (today's bookings must be reschedulable)

2. **Do NOT change** the `except_days` storage format without updating both backend and frontend

3. **Always test** print functionality after any table/styling changes

4. **Always verify** that filter dropdowns display correctly (no overlapping text)

5. **Always check** that totals rows are included when modifying report tables

6. The `serialize_booking_response()` function is critical for proper API responses - do not remove it

7. The `get_seva_safely()` function handles database schema evolution gracefully - maintain this pattern

---

## Files That Should NOT Be Modified Without Testing

### Critical Backend Files:
- `backend/app/api/sevas.py` - All booking and seva management logic
- `backend/app/api/reports.py` - All report generation logic
- `backend/app/models/seva.py` - Database models
- `backend/app/schemas/seva.py` - API schemas with validators

### Critical Frontend Files:
- `frontend/src/pages/SevaManagement.js` - Seva CRUD form
- `frontend/src/pages/DetailedSevaReport.js` - Seva report with filters
- `frontend/src/pages/DetailedDonationReport.js` - Donation report
- `frontend/src/index.css` - Print styles (lines in `@media print` section)

---

**⚠️ END OF FROZEN DOCUMENTATION ⚠️**







