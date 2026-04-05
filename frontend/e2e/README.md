# Playwright E2E

This folder contains browser-level smoke coverage for the MandirMitra frontend against the unified `sanmitra-backend` contract:
- login and protected-route redirect
- dashboard
- donations
- sevas
- inventory
- HR
- UPI/payment logging
- accounting reports
- panchang

For the broader multi-frontend plan, see `docs/UNIFIED_E2E_STRATEGY.md`.

## Setup

1. Install Playwright test runner:
   `npm install`
2. Install the browser runtime:
   `npx playwright install chromium`
3. Copy `.env.e2e.example` values into your shell or an env file and set real credentials for an already-onboarded account.
4. Optionally set `PLAYWRIGHT_APP_NAME` and `PLAYWRIGHT_APP_VARIANT` to select a UI selector profile when testing a non-MandirMitra frontend.

## Run

- Local frontend auto-start: `npm run test:e2e`
- Headed browser: `npm run test:e2e:headed`
- Playwright UI mode: `npm run test:e2e:ui`

## Notes

- By default the Playwright config starts the React frontend and points it at `PLAYWRIGHT_BACKEND_URL`.
- Set `PLAYWRIGHT_SKIP_WEBSERVER=1` if the frontend is already running.
- Use `PLAYWRIGHT_APP_NAME` and `PLAYWRIGHT_APP_VARIANT` to label and override selector profiles across the shared frontend matrix.
- The login helper fails fast if the account is redirected to `/setup-wizard`, because E2E should use a fully onboarded test tenant.
