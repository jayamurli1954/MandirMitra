# MandirMitra Phase-1 Go-Live Runbook

This runbook is for launching `v1.0` safely with phased delivery.

## 1) v1.0 Feature Freeze List

Only these modules are in scope for `v1.0`:

- Dashboard
- Donation
- Seva Booking
- Devotee Reports
- Accounting and Reports
- Panchang
- User Login and Roles
- Receipt generation (print/PDF)
- Backup and restore

Explicitly out of scope for `v1.0`:

- WhatsApp/SMS/Email receipts
- Payment gateway and QR donations
- Mobile app
- Inventory/Priest scheduling/Advanced automation

## 2) Go-Live Checklist

### Product Readiness

- [ ] All `v1.0` scope features tested end-to-end
- [ ] No open P0 or P1 defects
- [ ] Role access verified: Admin, Accountant, Data Entry, Viewer
- [ ] Receipt numbering and format verified
- [ ] Report totals reconciled with manual calculation (sample 7 days)

### Security and Compliance

- [ ] JWT auth enabled in production
- [ ] Password hashing enabled (`bcrypt`/`argon2`)
- [ ] CORS restricted to production frontend domains only
- [ ] Login and donation APIs rate-limited
- [ ] Security headers enabled
- [ ] Admin-only actions protected (delete/edit sensitive records)

### Data Safety

- [ ] Production DB backup completed before release
- [ ] Restore drill executed in non-prod successfully
- [ ] Backup retention policy documented
- [ ] Migration scripts tested on staging data

### Deployment Readiness

- [ ] Frontend environment variables validated
- [ ] Backend environment variables validated
- [ ] Health endpoint returns 200 (`/health`)
- [ ] Monitoring/alerts enabled (errors, latency, uptime)
- [ ] Release tag created (`v1.0.0`)

### Smoke Tests After Deployment

- [ ] Login works for each role
- [ ] Create devotee works
- [ ] Create donation + receipt works
- [ ] Create seva booking works
- [ ] Dashboard and key reports load in acceptable time
- [ ] Panchang view loads correctly

## 3) Rollback Plan

Use this if post-release checks fail.

### Trigger Conditions

- P0 outage or data corruption
- Persistent login or donation failure > 15 minutes
- Error rate spike and no fix-forward path in 30 minutes

### Rollback Steps

1. Put app in maintenance mode (if available).
2. Roll frontend to previous known-good deploy.
3. Roll backend to previous release image.
4. If migration broke data and is non-reversible, restore DB backup.
5. Verify `/health`, login, donation create, seva booking create.
6. Announce rollback completion and incident status.

### Rollback Ownership

- Incident Commander: `<name>`
- Backend owner: `<name>`
- Frontend owner: `<name>`
- DB owner: `<name>`

## 4) First 2 Weeks Hypercare Plan

### Week 1 (Daily)

- Track: error rate, p95 latency, API failures, DB CPU/memory
- Review donation/seva report mismatches
- Verify daily backup success and restore sample once
- Resolve all P1 issues within 24 hours

### Week 2 (Daily)

- Continue monitoring and trend analysis
- Prioritize fixes by user impact
- Freeze non-critical changes
- Prepare `v1.0.1` patch release window

### Hypercare SLAs

- P0: acknowledge in 15 minutes, restore service within 60 minutes
- P1: acknowledge in 1 hour, fix within 24 hours
- P2: plan in next patch cycle

## 5) Railway + Netlify Cutover Checklist (Optional)

Use this only if you choose to move from `Render + Vercel`.

### Pre-Cutover

- [ ] Railway project created for backend
- [ ] Netlify site created for frontend
- [ ] All environment variables migrated and validated
- [ ] CORS updated to include Netlify domain
- [ ] DNS and custom domain plan ready

### Repo Config Checks

- [ ] `railway.toml` start command and health path verified
- [ ] `netlify.toml` build settings validated
- [ ] React SPA redirect rule confirmed

### Production Switch

- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Netlify
- [ ] Run smoke tests
- [ ] Shift DNS traffic
- [ ] Monitor closely for 24 hours

## 6) Release Record

- Release version:
- Release date:
- Release owner:
- Go/no-go decision:
- Notes:
