# Vercel Deployment

## Project Setup
- Import the repository into Vercel.
- Set the Root Directory to `frontend`.
- Framework Preset: `Create React App` if Vercel detects it, otherwise `Other`.
- Build Command: `npm run build`
- Output Directory: `build`
- Install Command: `npm ci`

## Environments
- Production Branch: `main`
- Testing/Staging Branch: `develop`
- Feature branches: optional preview deployments

## Required Environment Variables
Set these for both Preview and Production environments:

```
REACT_APP_API_URL=https://mandirmitra-backend.onrender.com
REACT_APP_FALLBACK_API_URL=https://mandirmitra-backend.onrender.com
```

## Notes
- The frontend is configured to call the backend directly on Vercel.
- `frontend/vercel.json` handles SPA route rewrites and response headers.
- Keep day-to-day testing on `develop`; merge to `main` only when you want a production publish.
- If you want the testing site restricted, enable Vercel preview protection in the project settings.
