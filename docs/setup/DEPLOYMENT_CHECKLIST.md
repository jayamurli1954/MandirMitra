# Deployment Checklist

Use this checklist before deploying to production.

## Pre-Deployment

### Code Quality
- [ ] All tests pass locally
- [ ] All tests pass in CI/CD (if configured)
- [ ] Code review approved by at least 1 reviewer
- [ ] No linter errors
- [ ] No type errors (mypy/TypeScript)

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed on staging
- [ ] Edge cases tested
- [ ] Error scenarios tested

### Database
- [ ] Database migrations created (if needed)
- [ ] Migrations tested on staging
- [ ] Migrations are reversible
- [ ] Backup strategy confirmed

### Documentation
- [ ] API documentation updated (if API changes)
- [ ] User documentation updated (if UI changes)
- [ ] Changelog updated
- [ ] Migration guide created (if breaking changes)

## Deployment

### Preparation
- [ ] Deployment window scheduled (if needed)
- [ ] Team notified of deployment
- [ ] Rollback plan documented
- [ ] Database backup created

### Execution
- [ ] Stop services
- [ ] Backup current code version (git tag)
- [ ] Deploy new code
- [ ] Run database migrations (if any)
- [ ] Start services
- [ ] Verify services are running

### Verification
- [ ] Health check endpoint returns 200
- [ ] Key features tested manually
- [ ] Error logs checked (no new errors)
- [ ] Performance metrics normal
- [ ] Database queries working

## Post-Deployment

### Monitoring (First 30 minutes)
- [ ] Monitor error rates
- [ ] Monitor response times
- [ ] Check application logs
- [ ] Monitor database performance
- [ ] Watch for user reports

### Monitoring (First 24 hours)
- [ ] Daily error report reviewed
- [ ] Performance metrics reviewed
- [ ] User feedback collected
- [ ] Any issues documented

## Rollback Plan

If issues are detected:

1. **Assess Severity**
   - P0 (Critical): Rollback immediately
   - P1 (High): Rollback if fix > 30 minutes
   - P2/P3: Fix forward if possible

2. **Execute Rollback**
   ```bash
   # Stop services
   # Restore previous version
   git checkout <previous-tag>
   # Restore database (if needed)
   # Start services
   # Verify health
   ```

3. **Document**
   - Create incident report
   - Schedule post-mortem
   - Update deployment notes

## Notes

**Date:** _______________  
**Deployed By:** _______________  
**Version:** _______________  
**Issues Encountered:** _______________


