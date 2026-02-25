# CI/CD Guide for MandirMitra

**Last Updated:** 2025-12-25  
**Purpose:** Establish Continuous Integration and Continuous Deployment workflows for MandirMitra

---

## Table of Contents

1. [What is CI/CD in MandirMitra Context?](#what-is-cicd-in-mandirmitra-context)
2. [CI/CD Architecture](#cicd-architecture)
3. [CI Pipeline (Continuous Integration)](#ci-pipeline-continuous-integration)
4. [CD Pipeline (Continuous Deployment)](#cd-pipeline-continuous-deployment)
5. [Implementation Guide](#implementation-guide)
6. [Deployment Strategies](#deployment-strategies)
7. [Monitoring & Rollback](#monitoring--rollback)

---

## What is CI/CD in MandirMitra Context?

### CI (Continuous Integration)
**What it does:** Automatically tests and validates code when developers push changes.

**In MandirMitra:**
- When you push code to GitHub/GitLab, CI automatically:
  - Runs pre-commit hooks (black, flake8, eslint)
  - Runs unit tests (backend + frontend)
  - Runs integration tests
  - Checks code quality
  - Builds the application
  - Creates test reports

**Benefits:**
- Catch bugs before they reach production
- Ensure code quality standards
- Prevent broken code from being merged

### CD (Continuous Deployment)
**What it does:** Automatically deploys code to production after CI passes.

**In MandirMitra:**
- After CI passes, CD automatically:
  - Builds production-ready packages
  - Deploys to staging environment (for testing)
  - Deploys to production (if staging tests pass)
  - Creates standalone packages for distribution
  - Updates documentation

**Benefits:**
- Faster delivery of features
- Consistent deployments
- Reduced human error
- Automated rollback on failure

---

## CI/CD Architecture

### For MandirMitra, we have two deployment models:

#### 1. **Standalone Package Distribution**
```
Developer Push → CI Tests → Build Standalone Package → Upload to Distribution Server
```

#### 2. **SaaS Cloud Deployment**
```
Developer Push → CI Tests → Deploy to Staging → Test → Deploy to Production
```

### Recommended Tools

**Option 1: GitHub Actions** (Recommended - Free for public repos)
- ✅ Integrated with GitHub
- ✅ Free for public repositories
- ✅ Easy to set up
- ✅ Good documentation

**Option 2: GitLab CI/CD**
- ✅ Built into GitLab
- ✅ Free for private repos
- ✅ More advanced features

**Option 3: Jenkins** (Self-hosted)
- ✅ Full control
- ✅ Free and open-source
- ⚠️ Requires server setup

---

## CI Pipeline (Continuous Integration)

### Workflow Overview

```
┌─────────────────┐
│  Code Push      │
│  (Git Push)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Pre-commit     │
│  Hooks          │
│  (Local)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CI Pipeline    │
│  (GitHub/GitLab)│
└────────┬────────┘
         │
         ├─► Lint & Format (black, flake8, eslint)
         ├─► Unit Tests (pytest, jest)
         ├─► Integration Tests
         ├─► Build Backend
         ├─► Build Frontend
         └─► Generate Test Reports
         │
         ▼
    ┌────────┐
    │ Pass?  │
    └───┬────┘
        │
    Yes │ No
        │ └─► Notify Developer
        │
        ▼
┌─────────────────┐
│  Ready for CD    │
└─────────────────┘
```

### CI Steps (Detailed)

#### Step 1: Code Quality Checks
```yaml
- name: Format Python code
  run: black --check backend/

- name: Lint Python code
  run: flake8 backend/

- name: Lint JavaScript code
  run: cd frontend && npm run lint
```

#### Step 2: Run Tests
```yaml
- name: Run Backend Tests
  run: |
    cd backend
    pytest tests/ --cov=app --cov-report=xml

- name: Run Frontend Tests
  run: |
    cd frontend
    npm test -- --coverage
```

#### Step 3: Build Applications
```yaml
- name: Build Backend
  run: |
    cd backend
    pip install -r requirements.txt
    # Verify imports work
    python -c "import app.main"

- name: Build Frontend
  run: |
    cd frontend
    npm install
    npm run build
```

#### Step 4: Security Checks (Optional but Recommended)
```yaml
- name: Security Scan
  run: |
    pip install safety
    safety check -r backend/requirements.txt
```

---

## CD Pipeline (Continuous Deployment)

### Deployment Strategies

#### Strategy 1: Standalone Package Distribution

**Use Case:** Distributing Windows installer/portable package to temples

**Workflow:**
```
CI Passes → Build Standalone Package → Upload to Cloud Storage → Notify Users
```

**Steps:**
1. Build executable using PyInstaller (or similar)
2. Package frontend build
3. Create installer
4. Upload to distribution server (AWS S3, Google Drive, etc.)
5. Update download links

#### Strategy 2: SaaS Cloud Deployment

**Use Case:** Cloud-hosted version for temples

**Workflow:**
```
CI Passes → Deploy to Staging → Run E2E Tests → Deploy to Production
```

**Steps:**
1. Build Docker images
2. Deploy to staging environment
3. Run smoke tests
4. If tests pass, deploy to production
5. Health check and monitoring

---

## Implementation Guide

### Option 1: GitHub Actions (Recommended)

#### Setup Steps

1. **Create `.github/workflows/ci.yml`**

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Format check (black)
        run: |
          cd backend
          black --check app/
      
      - name: Lint (flake8)
        run: |
          cd backend
          flake8 app/ --max-line-length=100 --exclude=migrations,venv
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Lint
        run: |
          cd frontend
          npm run lint
      
      - name: Build
        run: |
          cd frontend
          npm run build
      
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false

  build-packages:
    needs: [backend-tests, frontend-tests]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Standalone Package
        run: |
          # Your build script here
          echo "Building standalone package..."
      
      - name: Upload Artifact
        uses: actions/upload-artifact@v3
        with:
          name: standalone-package
          path: dist/
```

2. **Create `.github/workflows/cd.yml`** (for production deployment)

```yaml
name: CD Pipeline

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Staging
        run: |
          echo "Deploying to staging..."
          # Your deployment script here
      
      - name: Run Smoke Tests
        run: |
          echo "Running smoke tests..."
          # Your smoke test script here

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    if: startsWith(github.ref, 'refs/tags/v')
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Production
        run: |
          echo "Deploying to production..."
          # Your deployment script here
      
      - name: Health Check
        run: |
          echo "Checking production health..."
          # Your health check script here
```

### Option 2: GitLab CI/CD

#### Create `.gitlab-ci.yml`

```yaml
stages:
  - test
  - build
  - deploy

variables:
  POSTGRES_DB: test_db
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres

backend-tests:
  stage: test
  image: python:3.11
  services:
    - postgres:14
  before_script:
    - cd backend
    - pip install -r requirements.txt
  script:
    - black --check app/
    - flake8 app/ --max-line-length=100
    - pytest tests/ --cov=app
  coverage: '/TOTAL.*\s+(\d+%)$/'

frontend-tests:
  stage: test
  image: node:18
  before_script:
    - cd frontend
    - npm ci
  script:
    - npm run lint
    - npm run build
    - npm test -- --coverage --watchAll=false

build-package:
  stage: build
  image: ubuntu:latest
  script:
    - echo "Building standalone package..."
    # Your build commands here
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  only:
    - main

deploy-staging:
  stage: deploy
  script:
    - echo "Deploying to staging..."
  environment:
    name: staging
    url: https://staging.mandirmitra.com
  only:
    - main

deploy-production:
  stage: deploy
  script:
    - echo "Deploying to production..."
  environment:
    name: production
    url: https://mandirmitra.com
  when: manual
  only:
    - tags
```

---

## Deployment Strategies

### 1. Blue-Green Deployment

**Best for:** Zero-downtime production deployments

**How it works:**
- Run two identical production environments (Blue and Green)
- Deploy new version to inactive environment
- Test the new environment
- Switch traffic from Blue → Green (or vice versa)
- Keep old environment for quick rollback

**For MandirMitra:**
```yaml
# Deploy to green environment
- Deploy new version to green
- Run health checks
- Switch load balancer to green
- Monitor for 5 minutes
- If issues, switch back to blue
```

### 2. Canary Deployment

**Best for:** Gradual rollout to minimize risk

**How it works:**
- Deploy new version to small subset of users (e.g., 10%)
- Monitor for issues
- Gradually increase to 50%, then 100%
- If issues found, rollback immediately

**For MandirMitra:**
```yaml
# Canary deployment
- Deploy to 10% of temples
- Monitor error rates
- If stable, increase to 50%
- If stable, deploy to 100%
```

### 3. Rolling Deployment

**Best for:** Simple, straightforward deployments

**How it works:**
- Deploy new version to one server at a time
- Wait for health check
- Move to next server
- Continue until all servers updated

---

## Monitoring & Rollback

### Health Checks

**Backend Health Check:**
```python
# backend/app/api/health.py
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": check_database(),
        "version": settings.APP_VERSION
    }
```

**Frontend Health Check:**
```javascript
// Check if API is reachable
fetch('/api/v1/health')
  .then(res => res.json())
  .then(data => console.log('Backend health:', data));
```

### Automated Rollback

**Trigger Conditions:**
- Error rate > 5%
- Response time > 2 seconds
- Database connection failures
- Health check failures

**Rollback Steps:**
```yaml
- name: Check Health
  run: |
    response=$(curl -s https://mandirmitra.com/api/v1/health)
    if [ "$response" != "healthy" ]; then
      echo "Health check failed, rolling back..."
      # Rollback script
    fi
```

---

## MandirMitra-Specific Considerations

### 1. Standalone Package Distribution

**CI/CD for Standalone Packages:**

```yaml
build-standalone:
  runs-on: windows-latest
  steps:
    - name: Build Windows Installer
      run: |
        # Build backend executable
        pyinstaller backend/app/main.py
        
        # Build frontend
        cd frontend && npm run build
        
        # Create installer
        # Package everything
        
    - name: Upload to Distribution Server
      run: |
        # Upload to S3/Google Drive/etc.
        aws s3 cp dist/MandirMitra-Setup.exe s3://mandirmitra-releases/
```

### 2. Database Migrations

**Important:** Always test migrations in CI before deploying

```yaml
- name: Test Migrations
  run: |
    cd backend
    alembic upgrade head
    alembic downgrade -1
    alembic upgrade head
```

### 3. License System

**Consideration:** License checks should not block CI/CD

```python
# In CI, disable license checks
if os.environ.get('CI'):
    settings.DEBUG = True  # Disables license checks
```

### 4. Multi-Tenant Deployment

**For SaaS version:**
- Deploy to staging first
- Test with test temple
- Deploy to production
- Monitor all temples

---

## Quick Start: Setting Up CI/CD

### Step 1: Choose Your Platform

**GitHub Actions (Recommended):**
```bash
mkdir -p .github/workflows
# Create ci.yml and cd.yml files (see examples above)
```

**GitLab CI:**
```bash
# Create .gitlab-ci.yml in root directory
```

### Step 2: Configure Secrets

**GitHub Actions:**
- Go to Repository → Settings → Secrets
- Add secrets:
  - `DATABASE_URL` (for tests)
  - `AWS_ACCESS_KEY_ID` (for deployment)
  - `AWS_SECRET_ACCESS_KEY`
  - `DEPLOYMENT_TOKEN`

**GitLab CI:**
- Go to Settings → CI/CD → Variables
- Add same secrets

### Step 3: Test Locally First

```bash
# Test CI steps locally
cd backend
black --check app/
flake8 app/
pytest tests/

cd frontend
npm run lint
npm run build
npm test
```

### Step 4: Push and Monitor

```bash
git add .
git commit -m "Add CI/CD pipeline"
git push origin main
```

Monitor the CI/CD pipeline in:
- **GitHub:** Actions tab
- **GitLab:** CI/CD → Pipelines

---

## Best Practices for MandirMitra

### 1. **Always Test Database Migrations**
- Run migrations in CI
- Test rollback procedures
- Never deploy untested migrations

### 2. **Version Your Releases**
- Use semantic versioning (v1.0.0, v1.1.0, etc.)
- Tag releases in Git
- Create release notes

### 3. **Separate Environments**
- **Development:** Local development
- **Staging:** Pre-production testing
- **Production:** Live system

### 4. **Automated Testing**
- Unit tests for critical functions (accounting, donations)
- Integration tests for API endpoints
- E2E tests for critical user flows

### 5. **Security First**
- Never commit secrets to Git
- Use environment variables
- Scan dependencies for vulnerabilities

### 6. **Documentation**
- Update CHANGELOG.md on each release
- Document breaking changes
- Update user guides

---

## Example: Complete CI/CD Workflow

### Scenario: Deploying a New Feature

1. **Developer pushes code:**
   ```bash
   git push origin feature/new-account-type
   ```

2. **CI Pipeline runs:**
   - ✅ Code formatting check
   - ✅ Linting
   - ✅ Unit tests (all pass)
   - ✅ Integration tests (all pass)
   - ✅ Build succeeds

3. **Pull Request created:**
   - CI runs again on PR
   - Code review by team
   - PR approved and merged

4. **CD Pipeline triggers:**
   - Deploy to staging
   - Run smoke tests
   - Manual approval for production

5. **Production deployment:**
   - Deploy to production
   - Health checks pass
   - Monitor for 30 minutes
   - If issues, automatic rollback

---

## Troubleshooting CI/CD

### Common Issues

**1. Tests failing in CI but passing locally:**
- Check environment variables
- Verify database setup
- Check Python/Node versions match

**2. Build failing:**
- Check dependencies are in requirements.txt/package.json
- Verify all files are committed
- Check for missing environment variables

**3. Deployment failing:**
- Check deployment credentials
- Verify target server is accessible
- Check disk space and permissions

---

## Next Steps

1. **Start Simple:**
   - Set up basic CI (tests + linting)
   - Add CD later

2. **Gradual Enhancement:**
   - Add more test coverage
   - Add security scanning
   - Add performance testing

3. **Monitor and Improve:**
   - Track CI/CD success rate
   - Optimize pipeline speed
   - Add more automation

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [React Deployment Guide](https://create-react-app.dev/docs/deployment/)

---

**Remember:** CI/CD is about automation and confidence. Start simple, iterate, and improve over time!


