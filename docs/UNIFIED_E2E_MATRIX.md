# Unified Frontend E2E Matrix

This matrix is the deployment-level companion to the shared `sanmitra-backend` contract.

## Matrix dimensions

- App name: human label for reporting
- App variant: selector profile key used by the Playwright helpers
- Frontend URL: deployed Vercel URL for the specific frontend
- Backend URL: unified `sanmitra-backend` URL
- Selector overrides: optional environment variables for app-specific labels

## Proposed applications

| App | Variant | Frontend URL env | Backend URL env | Notes |
| --- | --- | --- | --- | --- |
| MandirMitra | `mandirmitra` | `MANDIRMITRA_FRONTEND_URL` | `SANMITRA_BACKEND_URL` | Baseline selector profile in this repo |
| LegalMitra | `legalmitra` | `LEGALMITRA_FRONTEND_URL` | `SANMITRA_BACKEND_URL` | Use the same backend contract, override selectors if labels differ |
| GruhaMitra | `gruhamitra` | `GRUHAMITRA_FRONTEND_URL` | `SANMITRA_BACKEND_URL` | Old GharMitra rename path |
| InvestMitra | `investmitra` | `INVESTMITRA_FRONTEND_URL` | `SANMITRA_BACKEND_URL` | Use the unified backend auth/session contract |
| Shared/Other | `shared` | `SHARED_FRONTEND_URL` | `SANMITRA_BACKEND_URL` | Reserve for the remaining frontend in the program |

## Workflow behavior

- Run the backend contract smoke first with Newman/Postman.
- Run Playwright against each frontend URL using the same backend URL.
- Use `PLAYWRIGHT_APP_VARIANT` to select or override UI selector labels.
- Skip a matrix row automatically when its frontend URL env var is empty.

## Failure interpretation

- If all apps fail in the same way, check the shared backend or deployment cache.
- If only one app fails, treat it as a frontend-specific selector or deployment issue.
- If the report or donation flow fails only in one app, compare its env vars and build output against the others.
