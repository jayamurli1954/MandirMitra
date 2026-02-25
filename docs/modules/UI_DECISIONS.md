# UI Design Decisions & History

This file tracks UI/UX decisions and changes made to the MandirSync frontend.

## Last Updated: November 22, 2025

---

## Dashboard Layout

### Current Design (November 2025)

**Layout Structure:**
- Top Section: 4 stat cards in a row
  - Today's Donations
  - Total Devotees
  - Seva Bookings
  - This Month
- Bottom Section: 2-column layout
  - Left: Quick Donation Entry Form
  - Right: Today's Panchang Widget

**Features:**
- ✅ Donation entry form directly on dashboard
- ✅ Panchang display widget on dashboard
- ✅ Real-time stats from backend API
- ✅ Temple gopuram icon in sidebar header

---

## Header & Branding

### Sidebar Header
- **Background Color:** #FF9933 (Saffron)
- **Logo:** Temple Gopuram SVG icon (32x32px)
- **Text:** "MandirSync" in white, bold
- **Location:** Left sidebar top section

### Temple Gopuram Icon
- **File:** `/frontend/public/temple-gopuram.svg`
- **Style:** Simple geometric temple gopuram shape
- **Colors:** Saffron (#FF9933) with gold accents
- **Size:** 32x32 pixels
- **Display:** White (inverted) when used in sidebar

---

## Color Scheme

### Primary Colors
- **Saffron (Primary):** #FF9933 - Used for headers, buttons, accents
- **Green (Secondary):** #138808 - Used for success states, positive indicators
- **Red (Error):** #DC3545 - Used for errors, warnings
- **Blue (Info):** #2196F3 - Used for information, links

### Background Colors
- **Main Background:** #f5f5f5 (Light gray)
- **Card Background:** #ffffff (White)
- **Panchang Widget:** #FFF9E6 (Light yellow/cream)

---

## Navigation Structure

### Sidebar Menu Items (in order):
1. Dashboard
2. Donations
3. Devotees
4. Reports
5. Panchang
6. Settings

### Active State
- Background: #FFF3E0 (Light orange)
- Left border: 4px solid #FF9933
- Icon color: #FF9933

---

## Donation Entry

### Dashboard Quick Entry Form
- **Location:** Left column of bottom section
- **Fields:**
  - Devotee Name (required)
  - Phone Number (required, max 10 digits)
  - Amount (required, number input)
  - Category (dropdown, required)
  - Payment Mode (dropdown, required)
- **Categories:** General Donation, Annadanam, Construction Fund, Gold/Silver Donation, Corpus Fund
- **Payment Modes:** Cash, Card, UPI, Cheque, Online
- **Submit Button:** Full width, saffron color

### Donations Page
- **Multiple Entry Form:** Up to 5 donations at once
- **Each Entry:** Same fields as quick entry
- **Add/Remove:** Buttons to add or remove entry rows
- **Save All:** Single button to save all entries

---

## Panchang Display

### Dashboard Widget
- **Location:** Right column of bottom section
- **Background:** #FFF9E6 (Light yellow/cream)
- **Shows:**
  - Today's date (formatted)
  - Tithi (when available)
  - Nakshatra (when available)
  - Rahu Kaal warning (if applicable)
  - Abhijit Muhurat highlight (if applicable)
- **Link:** Button to view full panchang page

### Full Panchang Page
- **Location:** `/panchang` route
- **Features:**
  - Complete panchang details
  - Display settings configuration
  - Link to settings page

---

## Component Structure

### Layout Component
- **File:** `frontend/src/components/Layout.js`
- **Features:**
  - Sidebar navigation
  - Top app bar
  - User menu with logout
  - Responsive design (mobile drawer)

### Protected Routes
- **File:** `frontend/src/components/ProtectedRoute.js`
- **Function:** Redirects to login if not authenticated

---

## API Integration

### API Service
- **File:** `frontend/src/services/api.js`
- **Base URL:** `http://localhost:8000` (configurable via env)
- **Features:**
  - Automatic token injection
  - Error handling
  - 401 redirect to login

### Endpoints Used:
- `/api/v1/donations` - Donation CRUD
- `/api/v1/devotees` - Devotee CRUD
- `/api/v1/panchang/display-settings/` - Panchang settings
- `/api/v1/donations/report/daily` - Daily reports
- `/api/v1/donations/report/monthly` - Monthly reports

---

## Future Improvements

### Planned Enhancements:
- [ ] Add temple logo upload functionality
- [ ] Customizable dashboard widgets
- [ ] Dark mode support
- [ ] Multi-language support (Hindi, Tamil, Telugu, etc.)
- [ ] Print-friendly panchang view
- [ ] Mobile-responsive improvements
- [ ] Offline support for donation entry

---

## Notes

- All UI decisions should be documented here
- When making changes, update this file
- Reference this file when asking about previous UI implementations
- Keep screenshots or mockups in `/docs/ui-mockups/` if created

