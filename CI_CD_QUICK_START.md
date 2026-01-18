# CI/CD Quick Start Guide for MandirMitra

## What is CI/CD?

**CI (Continuous Integration):** Automatically test your code when you push changes  
**CD (Continuous Deployment):** Automatically deploy your code after tests pass

## For MandirMitra, CI/CD Means:

### When You Push Code:
1. ✅ **Automatically runs tests** (backend + frontend)
2. ✅ **Checks code quality** (linting, formatting)
3. ✅ **Builds the application** (verifies it compiles)
4. ✅ **Deploys to staging** (for testing)
5. ✅ **Deploys to production** (if staging passes)

### Benefits:
- 🐛 **Catch bugs early** - Before they reach production
- ⚡ **Faster releases** - Automated deployment saves time
- 🔒 **Safer deployments** - Tests must pass before deployment
- 📊 **Better quality** - Consistent code standards

---

## Quick Setup (5 Minutes)

### Option 1: GitHub Actions (Recommended)

**Already configured!** The files are in `.github/workflows/`:
- `ci.yml` - Runs tests on every push
- `cd.yml` - Deploys after tests pass

**To activate:**
1. Push code to GitHub
2. Go to your repository → **Actions** tab
3. CI/CD will run automatically!

**No additional setup needed** - GitHub Actions is free for public repos.

### Option 2: GitLab CI/CD

1. Create `.gitlab-ci.yml` in root directory (see `CI_CD_GUIDE.md`)
2. Push to GitLab
3. CI/CD runs automatically

---

## What Happens in CI Pipeline?

### Step 1: Code Quality
```bash
✅ Format check (black)
✅ Lint check (flake8, eslint)
✅ Type checking (mypy, TypeScript)
```

### Step 2: Testing
```bash
✅ Backend unit tests (pytest)
✅ Frontend unit tests (jest)
✅ Integration tests
✅ Coverage reports
```

### Step 3: Build
```bash
✅ Build backend (verify imports)
✅ Build frontend (npm run build)
✅ Create standalone package (if on main branch)
```

---

## What Happens in CD Pipeline?

### For Standalone Packages:
```
✅ Build Windows installer
✅ Package frontend build
✅ Upload to distribution server
✅ Update download links
```

### For SaaS Deployment:
```
✅ Deploy to staging
✅ Run smoke tests
✅ Deploy to production (if staging passes)
✅ Health check
✅ Monitor for issues
```

---

## Current Status

### ✅ Already Set Up:
- Pre-commit hooks (local testing)
- Code formatters (black, prettier)
- Linters (flake8, eslint)
- Test frameworks (pytest, jest)

### Next Steps:
1. **Enable GitHub Actions** (if using GitHub)
   - Push code to GitHub
   - Actions will run automatically

2. **Configure Deployment** (optional)
   - Add deployment scripts to `cd.yml`
   - Set up staging/production environments
   - Configure secrets (API keys, etc.)

3. **Add More Tests** (gradually)
   - Start with critical features (accounting, donations)
   - Add tests as you work on features
   - Aim for 70%+ coverage

---

## Example Workflow

### Scenario: Adding a New Feature

1. **You write code:**
   ```bash
   git add .
   git commit -m "Add new expense account autocomplete"
   ```

2. **Pre-commit hooks run** (local):
   - ✅ Formats code
   - ✅ Lints code
   - ✅ Basic checks

3. **You push to GitHub:**
   ```bash
   git push origin feature/new-feature
   ```

4. **CI Pipeline runs** (automatic):
   - ✅ Tests run
   - ✅ Code quality checks
   - ✅ Build verification

5. **Create Pull Request:**
   - CI runs again on PR
   - Team reviews code
   - PR approved and merged

6. **CD Pipeline runs** (automatic):
   - ✅ Deploys to staging
   - ✅ Smoke tests
   - ✅ Ready for production

---

## Monitoring CI/CD

### GitHub Actions:
- Go to repository → **Actions** tab
- See all pipeline runs
- Click on a run to see details
- Green ✅ = Passed
- Red ❌ = Failed (click to see errors)

### GitLab CI:
- Go to **CI/CD → Pipelines**
- See all pipeline runs
- Click to see details

---

## Troubleshooting

### CI Failing?

**Common causes:**
1. **Tests failing:**
   - Check test output in Actions tab
   - Run tests locally: `pytest` or `npm test`
   - Fix failing tests

2. **Linting errors:**
   - Run locally: `black backend/` or `npm run lint:fix`
   - Fix formatting issues

3. **Build errors:**
   - Check dependencies in `requirements.txt` / `package.json`
   - Verify all files are committed

### CD Failing?

**Common causes:**
1. **Deployment credentials missing:**
   - Add secrets to GitHub/GitLab
   - Check deployment scripts

2. **Server not accessible:**
   - Check network connectivity
   - Verify server is running

---

## Best Practices

### 1. **Test Before Push**
```bash
# Run tests locally first
cd backend && pytest
cd frontend && npm test
```

### 2. **Small, Frequent Commits**
- Better than large commits
- Easier to debug if CI fails
- Faster feedback

### 3. **Fix CI Issues Immediately**
- Don't ignore failing CI
- Fix before merging
- Keeps main branch stable

### 4. **Monitor Deployments**
- Watch first 30 minutes after deployment
- Check error logs
- Monitor user feedback

---

## Next Steps

1. **Start Simple:**
   - Use the provided CI/CD files
   - Push code and watch it run
   - Fix any issues that come up

2. **Add More Tests:**
   - Write tests for new features
   - Increase coverage gradually
   - Focus on critical paths first

3. **Configure Deployment:**
   - Set up staging environment
   - Add deployment scripts
   - Test deployment process

4. **Monitor and Improve:**
   - Track CI/CD success rate
   - Optimize pipeline speed
   - Add more automation

---

## Resources

- **Full Guide:** See `CI_CD_GUIDE.md` for detailed information
- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **GitLab CI Docs:** https://docs.gitlab.com/ee/ci/

---

**Remember:** CI/CD is a journey, not a destination. Start simple and improve over time!


