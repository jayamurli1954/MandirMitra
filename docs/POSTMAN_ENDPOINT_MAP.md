# MandirMitra Postman Endpoint Map

This backend is API-driven. The FastAPI app mounts routers for auth, devotees, donations, sevas, accounting, reports, and related modules.

## Base Setup

- Base URL: `https://sanmitra-backend-staging-sg.onrender.com`
- Auth header: `Authorization: Bearer {{token}}`
- Tenant header: `X-Temple-Id: {{temple_id}}`
- App header: `X-App-Key: mandirmitra`
- Content-Type: `application/json`

## Postman Environment Variables

- `base_url`
- `token`
- `temple_id`
- `mobile`
- `pincode`
- `devotee_id`
- `seva_id`
- `booking_id`
- `account_id`
- `donation_id`

## Critical Flow Map

### 1. Authentication

- `POST {{base_url}}/api/v1/login`
- `POST {{base_url}}/api/v1/setup/bootstrap`
- `POST {{base_url}}/api/v1/forgot-password`
- `POST {{base_url}}/api/v1/reset-password`

Use this folder first so every later request can reuse the token.

### 2. Devotees

- `GET {{base_url}}/api/v1/devotees`
- `GET {{base_url}}/api/v1/devotees/search/by-mobile/{{mobile}}`
- `GET {{base_url}}/api/v1/devotees/{devotee_id}`
- `POST {{base_url}}/api/v1/devotees`
- `PUT {{base_url}}/api/v1/devotees/{devotee_id}`
- `DELETE {{base_url}}/api/v1/devotees/{devotee_id}`
- `POST {{base_url}}/api/v1/devotees/merge`
- `PUT {{base_url}}/api/v1/devotees/{devotee_id}/link-family`
- `PUT {{base_url}}/api/v1/devotees/{devotee_id}/tags`
- `GET {{base_url}}/api/v1/devotees/{devotee_id}/family`
- `POST {{base_url}}/api/v1/devotees/bulk-import`
- `GET {{base_url}}/api/v1/devotees/export-template`
- `GET {{base_url}}/api/v1/devotees/duplicates`
- `GET {{base_url}}/api/v1/devotees/birthdays`
- `GET {{base_url}}/api/v1/devotees/analytics`

### 3. Pincode Autofill

- `GET {{base_url}}/api/v1/pincode/lookup?pincode={{pincode}}`
- `GET {{base_url}}/api/v1/pincode/search?pincode={{pincode}}`

Note:
- The frontend currently calls `/api/v1/pincode/lookup`.
- This route is the one to verify for city/state autofill in production.
- If a direct request 404s, verify the deployed gateway rewrite before changing the collection.

### 4. Chart of Accounts

- `GET {{base_url}}/api/v1/accounts`
- `GET {{base_url}}/api/v1/accounts/hierarchy`
- `POST {{base_url}}/api/v1/accounts/initialize-default`
- `GET {{base_url}}/api/v1/accounts/{account_id}`
- `POST {{base_url}}/api/v1/accounts`
- `PUT {{base_url}}/api/v1/accounts/{account_id}`
- `GET {{base_url}}/api/v1/accounts/{account_id}/has-transactions`
- `DELETE {{base_url}}/api/v1/accounts/{account_id}`
- `GET {{base_url}}/api/v1/accounts/{account_id}/balance`

### 5. Donations

- `GET {{base_url}}/api/v1/donations/categories/`
- `GET {{base_url}}/api/v1/donations/payment-accounts`
- `GET {{base_url}}/api/v1/donations/bank-accounts`
- `POST {{base_url}}/api/v1/donations`
- `GET {{base_url}}/api/v1/donations`
- `GET {{base_url}}/api/v1/donations/{donation_id}`
- `PATCH {{base_url}}/api/v1/donations/{donation_id}`
- `GET {{base_url}}/api/v1/donations/{donation_id}/receipt/pdf`
- `GET {{base_url}}/api/v1/donations/report/daily`
- `GET {{base_url}}/api/v1/donations/report/monthly`
- `GET {{base_url}}/api/v1/donations/report/category-wise`
- `GET {{base_url}}/api/v1/donations/report/detailed`
- `GET {{base_url}}/api/v1/donations/export/pdf`
- `GET {{base_url}}/api/v1/donations/export/excel`
- `POST {{base_url}}/api/v1/donations/bulk-import`
- `POST {{base_url}}/api/v1/donations/bulk-80g-certificates`

### 6. Sevas

- `GET {{base_url}}/api/v1/sevas/`
- `GET {{base_url}}/api/v1/sevas/dropdown-options`
- `GET {{base_url}}/api/v1/sevas/payment-accounts`
- `GET {{base_url}}/api/v1/sevas/{seva_id}`
- `POST {{base_url}}/api/v1/sevas`
- `PUT {{base_url}}/api/v1/sevas/{seva_id}`
- `DELETE {{base_url}}/api/v1/sevas/{seva_id}`
- `GET {{base_url}}/api/v1/sevas/{seva_id}/available-dates`
- `GET {{base_url}}/api/v1/sevas/bookings/`
- `GET {{base_url}}/api/v1/sevas/bookings/{booking_id}`
- `POST {{base_url}}/api/v1/sevas/bookings/`
- `PUT {{base_url}}/api/v1/sevas/bookings/{booking_id}`
- `DELETE {{base_url}}/api/v1/sevas/bookings/{booking_id}`
- `PUT {{base_url}}/api/v1/sevas/bookings/{booking_id}/reschedule`
- `GET {{base_url}}/api/v1/sevas/reschedule/pending`
- `POST {{base_url}}/api/v1/sevas/bookings/{booking_id}/approve-reschedule`
- `GET {{base_url}}/api/v1/sevas/lists/priests`
- `PUT {{base_url}}/api/v1/sevas/bookings/{booking_id}/assign-priest`
- `PUT {{base_url}}/api/v1/sevas/bookings/{booking_id}/remove-priest`
- `POST {{base_url}}/api/v1/sevas/bookings/{booking_id}/process-refund`
- `GET {{base_url}}/api/v1/sevas/bookings/{booking_id}/refund-status`
- `GET {{base_url}}/api/v1/sevas/bookings/{booking_id}/receipt/pdf`
- `GET {{base_url}}/api/v1/sevas/bookings/{booking_id}/receipt/pdf-base64`
- `POST {{base_url}}/api/v1/sevas/bookings/transfer-advance-to-income`
- `POST {{base_url}}/api/v1/sevas/bookings/transfer-advance-batch`
- `POST {{base_url}}/api/v1/sevas/bookings/{booking_id}/create-accounting`

### 7. Journal Entries and Books

- `GET {{base_url}}/api/v1/journal-entries`
- `GET {{base_url}}/api/v1/journal-entries/{entry_id}`
- `POST {{base_url}}/api/v1/journal-entries`
- `PUT {{base_url}}/api/v1/journal-entries/{entry_id}`
- `DELETE {{base_url}}/api/v1/journal-entries/{entry_id}`
- `POST {{base_url}}/api/v1/journal-entries/{entry_id}/post`
- `POST {{base_url}}/api/v1/journal-entries/{entry_id}/cancel`
- `GET {{base_url}}/api/v1/journal-entries/reports/trial-balance`
- `GET {{base_url}}/api/v1/journal-entries/reports/ledger/{account_id}`
- `GET {{base_url}}/api/v1/journal-entries/reports/profit-loss`
- `GET {{base_url}}/api/v1/journal-entries/reports/category-income`
- `GET {{base_url}}/api/v1/journal-entries/reports/top-donors`
- `GET {{base_url}}/api/v1/journal-entries/reports/balance-sheet`
- `GET {{base_url}}/api/v1/journal-entries/reports/day-book`
- `GET {{base_url}}/api/v1/journal-entries/reports/cash-book`
- `GET {{base_url}}/api/v1/journal-entries/reports/bank-book`

### 8. Reports

- `GET {{base_url}}/api/v1/reports/donations/category-wise`
- `GET {{base_url}}/api/v1/reports/donations/detailed`
- `GET {{base_url}}/api/v1/reports/sevas/detailed`
- `GET {{base_url}}/api/v1/reports/sevas/schedule`
- `GET {{base_url}}/api/v1/reports/sevas/detailed/export/excel`
- `GET {{base_url}}/api/v1/reports/sevas/detailed/export/pdf`

## Recommended Postman Folder Order

1. Auth
2. Devotees
3. COA / Accounts
4. Donations
5. Sevas
6. Journal Entries
7. Reports

## Validation Targets For Smoke Testing

- Login returns a bearer token.
- Devotee search by mobile returns an existing devotee or an empty list.
- Pincode lookup returns city and state for a valid 6-digit PIN.
- COA initialization returns real account rows, not just a success message.
- Donation and seva payment-account endpoints return cash/bank options.
- Seva booking and donation booking both accept the selected devotee.
- Trial balance balances after posting the test journal entries.

