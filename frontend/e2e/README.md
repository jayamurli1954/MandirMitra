# Playwright E2E

This folder contains browser-level smoke coverage for the critical MandirMitra flows:
- login and protected-route redirect
- dashboard
- donations
- sevas
- inventory
- HR
- UPI/payment logging
- accounting reports
- panchang

## Setup

1. Install Playwright test runner:
   `npm install`
2. Install the browser runtime:
   `npx playwright install chromium`
3. Copy `.env.e2e.example` values into your shell or an env file and set real credentials for an already-onboarded account.

## Run

- Local frontend auto-start: `npm run test:e2e`
- Headed browser: `npm run test:e2e:headed`
- Playwright UI mode: `npm run test:e2e:ui`

## Notes

- By default the Playwright config starts the React frontend and points it at `PLAYWRIGHT_BACKEND_URL`.
- Set `PLAYWRIGHT_SKIP_WEBSERVER=1` if the frontend is already running.
- The login helper fails fast if the account is redirected to `/setup-wizard`, because E2E should use a fully onboarded test tenant.
