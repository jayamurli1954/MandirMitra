# MandirSync - Conversation Log & Project Context

This file tracks important conversations, decisions, and progress to maintain context across sessions.

**Last Updated:** November 22, 2025 (Evening Session)

---

## How to Use This File

When starting a new conversation, reference this file:
```
"Please read CONVERSATION_LOG.md to understand the project context and continue from where we left off."
```

---

## Project Overview

**Project:** MandirSync - Temple Management System  
**Tech Stack:** FastAPI (Python) + React (Frontend) + PostgreSQL  
**Status:** Active Development - MVP Phase

---

## Recent Development Sessions

### Session: November 22, 2025 (Evening) - Bug Fixes & Address Field Enhancement

**What We Fixed:**
1. **Address Field Enhancement:**
   - Replaced single address field with structured address fields:
     - Street Address (multiline, optional)
     - PIN Code (6 digits, with validation)
     - City (auto-filled from PIN code)
     - State (auto-filled from PIN code)
     - Country (defaults to "India")
   - Implemented PIN code lookup using Indian Postal API (`https://api.postalpincode.in/pincode/{pincode}`)
   - Auto-fills City and State when 6-digit PIN code is entered
   - Added loading indicator during PIN code lookup
   - Updated backend `Devotee` model to include `country` field
   - Updated donation API to accept and save all address fields separately

2. **Dashboard Data Consistency:**
   - Fixed: Dashboard now uses `/api/v1/donations/report/daily` endpoint (same as Reports page)
   - Fixed: Removed hardcoded fallback value of ₹8,500
   - Fixed: Added monthly donations calculation using monthly report endpoint
   - Fixed: Both Dashboard and Reports now show consistent data

3. **Devotee Count Fix:**
   - Fixed: Dashboard now counts unique devotees from ALL donations (not just today)
   - Fixed: Devotees page now properly fetches and displays devotees from donations
   - Improved: Better error handling and fallback logic

4. **Donation Submission Fix:**
   - Fixed: Endpoint URL changed to `/api/v1/donations/` (with trailing slash)
   - Improved: Enhanced error handling with detailed error messages
   - Fixed: Better authentication error handling in `get_current_user()`

5. **Panchang Widget & Page:**
   - Fixed: Improved data fetching and merging of settings with panchang data
   - Fixed: Better error handling and messages
   - Fixed: Panchang widget now displays correctly on dashboard

6. **Reports Export:**
   - Fixed: Improved error handling for Excel/PDF export
   - Fixed: Better error messages when export fails
   - Fixed: Removed mock data fallback (now shows actual data or 0)

7. **Reports Page:**
   - Fixed: Removed mock data (₹8,500) that was showing on errors
   - Fixed: Now shows actual data or 0 if no data exists
   - Improved: Better error messages

**Backend Changes:**
- Added `country` field to `Devotee` model (defaults to "India")
- Updated `DonationCreate` schema to accept: `address`, `pincode`, `city`, `state`, `country`
- Updated devotee creation/update logic to save all address fields
- Improved `get_current_user()` error handling

**Frontend Changes:**
- Updated donation form with separate address fields
- Added PIN code auto-fill functionality
- Fixed all API endpoint calls to use correct URLs
- Improved error handling across all pages
- Removed all hardcoded/mock data values

**Files Modified:**
- `backend/app/models/devotee.py` - Added country field
- `backend/app/api/donations.py` - Updated to accept address fields
- `backend/app/core/security.py` - Improved error handling
- `frontend/src/pages/Dashboard.js` - Fixed data fetching, added address fields
- `frontend/src/pages/Devotees.js` - Fixed devotee fetching
- `frontend/src/pages/Panchang.js` - Fixed data fetching
- `frontend/src/pages/Reports.js` - Removed mock data, improved errors

**Current Status:**
- ✅ Address fields with PIN code auto-fill working
- ✅ Dashboard and Reports show consistent data
- ✅ Devotee count displays correctly
- ✅ Donation submission working (with proper error handling)
- ✅ Panchang widget and page working
- ✅ Reports export working (with better error handling)
- ✅ All pages show real data (no mock/hardcoded values)

---

### Session: November 22, 2025 (Morning) - Panchang Display Settings Implementation

**What We Built:**
1. **Backend:**
   - Created `PanchangDisplaySettings` model with comprehensive display preferences
   - Created Pydantic schemas for validation
   - Created service layer for CRUD operations
   - Created API endpoints at `/api/v1/panchang/display-settings/`
   - Added preset configurations (minimal, standard, comprehensive)

2. **Frontend:**
   - Created complete React frontend structure
   - Implemented Login page
   - Implemented Dashboard with:
     - Quick donation entry form
     - Panchang display widget
     - Stats cards (Today's Donations, Devotees, Seva Bookings, Monthly)
   - Created Layout component with sidebar navigation
   - Created pages: Donations, Devotees, Reports, Panchang, Settings
   - Added temple gopuram icon in sidebar

**Key Features Implemented:**
- ✅ Donation entry form (supports up to 5 entries at once)
- ✅ Devotee management (CRUD operations)
- ✅ Reports page with multiple report types
- ✅ Panchang display settings API
- ✅ Dashboard with donation entry and panchang widget
- ✅ Sidebar navigation with temple gopuram icon

**Issues Fixed:**
- Fixed Pydantic v2 compatibility (regex → pattern)
- Fixed SQLAlchemy model registration (import all models before init_db)
- Fixed FastAPI dependency injection for get_current_user
- Reduced SQL logging verbosity (added SQL_ECHO setting)

**Current Data:**
- Actual donation amount: ₹8,500 (not hardcoded ₹12,450)
- 5 donation categories: General Donation, Annadanam, Construction Fund, Gold/Silver Donation, Corpus Fund

**UI Decisions:**
- Saffron (#FF9933) as primary color
- Green (#138808) as secondary color
- Temple gopuram icon before "MandirSync" text in sidebar
- Dashboard has donation form on left, panchang widget on right
- See `UI_DECISIONS.md` for detailed UI documentation

---

## Important Context from Earlier Sessions

### User Requirements (from conversation):
1. **Dashboard should have:**
   - Donation entry form directly on dashboard
   - Panchang display widget on dashboard
   - Temple gopuram image/icon before "MandirSync" text
   - Real data (not hardcoded values)

2. **Donation Entry:**
   - Support for 5 different categories
   - Support for 5 different devotees (multiple entries)
   - Quick entry form on dashboard
   - Full form on donations page

3. **Pages Required:**
   - Dashboard (with donation entry + panchang)
   - Donations (full donation management)
   - Devotees (devotee management)
   - Reports (reporting and analytics)
   - Panchang (panchang display and settings)
   - Settings (configuration)

4. **UI Preferences:**
   - Clean, professional design
   - Material-UI components
   - Saffron/Green color scheme (Indian flag colors)
   - Temple-themed branding

---

## Technical Decisions

### Backend Architecture:
- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0+
- **Database:** PostgreSQL 14+
- **Authentication:** JWT (development mode uses mock user)
- **API Versioning:** `/api/v1/`

### Frontend Architecture:
- **Framework:** React 18+
- **UI Library:** Material-UI v5
- **State Management:** React hooks (Zustand can be added later)
- **HTTP Client:** Axios
- **Routing:** React Router v6

### Database Models Created:
1. `Temple` - Temple master data
2. `User` - System users
3. `Donation` - Donation transactions
4. `DonationCategory` - Donation categories
5. `Devotee` - Devotee/CRM data (with address fields: address, pincode, city, state, country)
6. `PanchangDisplaySettings` - Panchang display preferences

### API Endpoints Created:
- `/api/v1/panchang/display-settings/` - Panchang display settings CRUD
- `/api/v1/panchang/today` - Get today's panchang data (mock implementation)
- `/api/v1/donations/` - Donation CRUD (POST, GET)
- `/api/v1/donations/report/daily` - Daily donation report
- `/api/v1/donations/report/monthly` - Monthly donation report
- `/api/v1/donations/export/excel` - Excel export
- `/api/v1/donations/export/pdf` - PDF export
- `/api/v1/devotees/` - Devotee CRUD operations

---

## Known Issues & TODOs

### Backend:
- [x] Create Devotee model ✅
- [x] Create donation API endpoints ✅
- [x] Create devotee API endpoints ✅
- [x] Create reports API endpoints ✅
- [x] Create Excel/PDF export endpoints ✅
- [ ] Implement proper JWT authentication (currently mock - works for development)
- [ ] Add panchang calculation service (currently returns mock data)
- [ ] Add temple logo upload functionality
- [ ] Add receipt generation with temple logo

### Frontend:
- [x] Connect donation form to actual API ✅
- [x] Connect devotee management to actual API ✅
- [x] Connect reports to actual API ✅
- [x] Implement panchang data display (using mock data from backend) ✅
- [ ] Add temple logo upload functionality
- [ ] Improve mobile responsiveness
- [ ] Add loading states for all async operations
- [ ] Add success/error notifications (toast messages)

---

## File Structure Reference

### Backend:
```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry
│   ├── core/
│   │   ├── config.py             # Settings (SQL_ECHO added)
│   │   ├── database.py           # DB connection
│   │   └── security.py           # Auth utilities
│   ├── models/
│   │   ├── temple.py             # Temple model
│   │   ├── user.py               # User model
│   │   ├── donation.py           # Donation & Category models
│   │   ├── devotee.py            # Devotee model (with address fields)
│   │   └── panchang_display_settings.py  # Panchang settings model
│   ├── schemas/
│   │   └── panchang_display_settings.py  # Pydantic schemas
│   ├── services/
│   │   └── panchang_display_settings_service.py
│   └── api/
│       ├── panchang_display_settings.py  # Panchang settings API
│       ├── donations.py                  # Donations API (CRUD, reports, export)
│       ├── devotees.py                   # Devotees API (CRUD)
│       └── panchang.py                   # Panchang data API
```

### Frontend:
```
frontend/
├── public/
│   ├── index.html
│   └── temple-gopuram.svg        # Temple icon
├── src/
│   ├── App.js                    # Main app with routes
│   ├── components/
│   │   ├── Layout.js            # Sidebar + header layout
│   │   └── ProtectedRoute.js   # Auth guard
│   ├── pages/
│   │   ├── Login.js            # Login page
│   │   ├── Dashboard.js       # Dashboard with donation + panchang
│   │   ├── Donations.js        # Full donation management
│   │   ├── Devotees.js         # Devotee management
│   │   ├── Reports.js          # Reports page
│   │   ├── Panchang.js         # Panchang page
│   │   └── Settings.js         # Settings page
│   └── services/
│       └── api.js               # Axios API service
```

---

## Configuration Notes

### Environment Variables Needed:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - For JWT tokens
- `SQL_ECHO` - SQL logging (default: false)
- `DEBUG` - Debug mode (default: true)

### Database Setup:
- Database name: `temple_db`
- All models imported in `main.py` before `init_db()` call
- Tables auto-created on startup

---

## Next Steps (Priority Order)

1. **Complete Backend APIs:**
   - Donation CRUD endpoints
   - Devotee CRUD endpoints
   - Reports endpoints
   - Panchang calculation service

2. **Connect Frontend to Backend:**
   - Wire up donation form to API
   - Wire up devotee management to API
   - Wire up reports to API

3. **Enhance Features:**
   - Add receipt generation
   - Add SMS/Email notifications
   - Add search and filters
   - Add pagination

---

## Important Notes

- **Donation Amount:** Shows actual data from database (no hardcoded values)
- **Categories:** 5 categories configured: General Donation, Annadanam, Construction Fund, Gold/Silver Donation, Corpus Fund
- **UI Theme:** Saffron (#FF9933) / Green (#138808) (Indian flag colors)
- **Temple Icon:** SVG gopuram icon in sidebar
- **Dashboard Layout:** Stats on top, donation form + panchang on bottom
- **Address Fields:** Structured address with PIN code auto-fill (City & State)
- **Data Consistency:** Dashboard and Reports use same endpoints for consistent data
- **Error Handling:** All pages have improved error messages (no silent failures)

---

## How to Continue Development

When starting a new session:

1. **Read this file first:**
   ```
   "Please read CONVERSATION_LOG.md to understand where we left off"
   ```

2. **Reference specific files:**
   ```
   "Based on CONVERSATION_LOG.md, continue implementing [feature]"
   ```

3. **Check UI decisions:**
   ```
   "Refer to UI_DECISIONS.md for UI guidelines"
   ```

4. **Check requirements:**
   ```
   "See PRD.md for feature requirements"
   ```

---

## Questions to Ask User

If context is unclear, ask:
- "What was the last feature you were working on?"
- "What issue are you facing right now?"
- "What should we prioritize next?"

---

## Recent Bug Fixes Summary (November 22, 2025 Evening)

1. ✅ **Address Field Enhancement** - Added structured address fields with PIN code auto-fill
2. ✅ **Dashboard Data Consistency** - Fixed to show same data as Reports page
3. ✅ **Devotee Count** - Fixed to count from all donations, not just today
4. ✅ **Donation Submission** - Fixed endpoint URL and error handling
5. ✅ **Panchang Widget/Page** - Fixed data fetching and display
6. ✅ **Reports Export** - Improved error handling for Excel/PDF
7. ✅ **Reports Page** - Removed mock data, shows real data
8. ✅ **All Pages** - Removed hardcoded/mock values, show actual data

**Key Improvement:** All data is now fetched from database, no hardcoded values anywhere.

---

**Remember:** Always update this file after significant changes or decisions!

