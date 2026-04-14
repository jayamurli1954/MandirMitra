# Changelog

All notable changes to MandirMitra are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- GitHub Actions CI/CD pipeline (lint, tests, security scan)
- Railway (`railway.toml`) and Netlify (`netlify.toml`) deployment configs
- Backend `Dockerfile` for Railway (multi-stage, non-root user)
- `.env.production.example` with full Neon + Railway + Netlify variable reference
- `SECURITY.md` with vulnerability reporting policy
- Refresh token expiry setting in config
- Account lockout (brute-force protection) config settings
- Per-endpoint auth rate limiting settings

### Fixed
- Removed duplicate `seva_exchange_router` import and registration in `main.py`
- Removed duplicate `EMAIL_ENABLED` and `SMS_PROVIDER` fields in `config.py` (caused Pydantic validation errors)
- Replaced deprecated `@app.on_event("startup")` with modern FastAPI `lifespan` context manager
- Swagger/ReDoc UI now hidden in production (`DEBUG=False`)

### Changed
- README updated: database corrected from MongoDB → PostgreSQL
- Root directory reorganized: 80+ `.md` files moved to `docs/` sub-folders
- `.gitignore` expanded: blocks all internal `.md` files, coverage reports, backup JSONs, SQLite files

---

## [1.2.0] - 2026-04-14

### STABLE RELEASE — Ready for Production

### Added
- **Quick Ticket Counter Mode** — Fast one-click seva booking without login (for temple counters)
- **Seva Renewal Reminders** — Automated email/SMS 1 month before seva subscription expiry
- **Public Payment Idempotency** — Prevents duplicate payments on network retry/double-tap
- **Formal Audit Logging** — All public payments logged with IP, timestamp, devotee details
- **Rate Limiting (slowapi)** — Public endpoints protected (10/min payments, 30/min sevas, 20/min autofill)
- **Indic Font Bundling** — Noto Sans fonts for Kannada, Devanagari, Tamil, Telugu, Malayalam (PDF rendering)
- **Multilingual Public Portal** — Complete i18n for PublicSevaPayment in English, Kannada, Hindi
- **Version Endpoint** — GET `/api/v1/mandir/version` returns deployed version + feature list

### Changed
- Backend version bumped from `0.1.0` → `1.2.0`
- Frontend version bumped from `1.0.1` → `1.2.0`
- Receipt PDF language override via `?lang=kannada|hindi|english` query param

### Fixed
- Corrected `/api/v1/public/` route prefix (was incorrectly `/api/v1/mandirmitra/public/`)
- Panchang date picker now respects "Today" button on manual date selection
- `Card` import error in Panchang page (Nakshatra Wizard now renders correctly)

### Security
- Added idempotency key validation to prevent replay attacks
- Public endpoints now rate-limited to prevent abuse
- All public payments now formally audited for compliance

---

## [1.0.0] - 2026-02-17

### Added
- Panchang engine (pyswisseph — Tithi, Nakshatra, Yoga, Karana)
- Devotee management & Ready Reckoner (birth star date finder)
- Donation tracking with PDF receipt generation
- Chart of Accounts (double-entry accounting)
- Journal entry & bank reconciliation module
- Asset management with depreciation
- Inventory management (stores, items, stock movements)
- Seva booking & advance booking transfer automation
- HR module (employees, payroll, leave)
- Hundi counting module
- Token seva management
- Budget & financial period closing
- In-kind donation & sponsorship modules
- UPI/bank payment tracking
- Role-based access control (Admin, Accountant, Priest, Viewer, Data Entry)
- JWT authentication with bcrypt password hashing
- Data encryption for sensitive fields
- Audit logging for financial operations
- Database integrity / tamper-detection checks
- Redis caching for Panchang pre-calculations
- Multi-language field support (Hindi, Kannada)
- Pincode master data integration
- PDF & Excel export for reports
- Backup & restore functionality
