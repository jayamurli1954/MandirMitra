# Unified E2E Strategy for sanmitra-backend

This repository already has a MandirMitra-specific Playwright suite. The unified backend changes the test boundary: the stable contract is now the backend API, while each frontend provides its own UI adapter and selectors.

## What to test centrally

These are backend-contract flows that should be shared across all five frontends:

- Authentication
- Temple context resolution
- Pincode lookup and city/state autofill
- Chart of accounts bootstrap and legacy import
- Devotee search/create
- Donation booking
- Seva booking
- Receipt generation
- Ledger posting
- Trial balance
- Report endpoints

## What to test per frontend

Each frontend should keep a thin UI smoke layer for the same backend flows, but with its own routes and selectors:

- MandirMitra
- LegalMitra
- GruhaMitra
- InvestMitra
- Any other app wired to `sanmitra-backend`

The UI checks should not duplicate business logic. They should verify that the frontend can drive the shared backend contract successfully.

## Recommended stack

### 1. Newman / Postman for backend contracts

Use this for strict API validation:

- login
- pincode lookup
- COA initialization/import
- donation create
- seva create
- ledger / trial balance

This is the fastest way to catch contract drift before the browser is involved.

### 2. Playwright for deterministic UI smoke

Use Playwright for one thin browser path per app:

- login
- one donation entry
- one seva booking
- one report load
- logout / session persistence check

Keep the assertions strict:

- expected title/heading exists
- expected API-derived data appears
- expected navigation path works
- session does not drop unexpectedly on normal usage

### 3. Autonoma for exploratory coverage

Use Autonoma as a regression discovery layer, not the primary gate.

Good uses:

- crawl each frontend against the same live backend
- discover broken links or blank screens
- spot contract mismatches that deterministic tests did not encode yet

Do not rely on Autonoma alone for accounting, donation posting, or trial balance validation. Those need hard assertions.

## Unified runtime variables

Every frontend E2E job should be driven by environment variables instead of hardcoded URLs:

- `PLAYWRIGHT_BASE_URL`
- `PLAYWRIGHT_BACKEND_URL`
- `PLAYWRIGHT_TEST_USERNAME`
- `PLAYWRIGHT_TEST_PASSWORD`
- `PLAYWRIGHT_TEMPLE_ID`
- `PLAYWRIGHT_APP_NAME`
- `PLAYWRIGHT_APP_VARIANT`

The backend URL should always point to the unified `sanmitra-backend` deployment for production-like smoke runs.

## Suggested rollout order

1. Lock the API contract with Newman/Postman.
2. Run one deterministic Playwright smoke per frontend.
3. Use Autonoma for exploratory coverage after the contract is stable.
4. Fail the deployment if any app regresses on login, donation, seva, or reports.

## Practical rule

If an issue is shared by all five apps, it is a backend or shared contract problem.
If an issue appears in only one app, it is a frontend adapter or deployment problem.

That split is the main reason the unified backend is workable: the contract is shared, the UI layer is app-specific.

## CI matrix

See `docs/UNIFIED_E2E_MATRIX.md` for the five-app deployment matrix and the environment variables that drive the shared Playwright suite.
