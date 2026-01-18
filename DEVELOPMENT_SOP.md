# Development Standard Operating Procedures (SOP)
## MandirMitra - FastAPI + React Application

**Last Updated:** 2025-12-25  
**Purpose:** Establish clear procedures to prevent bugs, ensure code quality, and maintain production stability.

---

## Table of Contents
1. [Pre-Development Phase](#pre-development-phase)
2. [Development Phase](#development-phase)
3. [Testing Phase](#testing-phase)
4. [Code Review Process](#code-review-process)
5. [Deployment Phase](#deployment-phase)
6. [Post-Deployment Monitoring](#post-deployment-monitoring)
7. [Incident Response](#incident-response)
8. [Tools & Configuration](#tools--configuration)

---

## Pre-Development Phase

### 1.1 Requirements & Design Documentation

**Before writing any code:**

- [ ] **Create/Update Issue/Feature Request**
  - Use clear, descriptive titles
  - Include: What, Why, Who, When
  - Add acceptance criteria (specific, testable)
  - Example: "Journal Entry Reversal: Ensure cancelled entries are excluded from trial balance"

- [ ] **Design Document Review**
  - For complex features (>50 lines of code), create a design doc
  - Include: Database schema changes, API endpoints, Frontend components
  - Review with team/stakeholder before coding

- [ ] **Impact Analysis**
  - List all affected modules/files
  - Identify potential breaking changes
  - Check for dependencies (other features using this code)

**Example Template:**
```markdown
## Feature: Journal Entry Reversal Fix

### Problem
Trial balance includes cancelled entries, causing incorrect balances.

### Solution
- Exclude CANCELLED status from trial balance queries
- Ensure reversal entries use same date as original entry

### Affected Files
- backend/app/api/journal_entries.py (get_trial_balance function)
- backend/app/api/journal_entries.py (cancel_journal_entry function)

### Database Changes
- None (using existing status field)

### API Changes
- None (backward compatible)

### Testing Requirements
- Unit test: cancelled entries excluded from trial balance
- Integration test: reversal entry date matches original
```

---

## Development Phase

### 2.1 Coding Standards

#### Python (Backend - FastAPI)

**File Structure:**
```python
"""
Module docstring - What this module does
"""
# Standard library imports
from datetime import datetime
from typing import List, Optional

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Local application imports
from app.core.database import get_db
from app.models.user import User
```

**Naming Conventions:**
- Functions: `snake_case` (e.g., `get_trial_balance`)
- Classes: `PascalCase` (e.g., `JournalEntry`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`)
- Private functions: `_leading_underscore` (e.g., `_validate_amount`)

**Code Quality Rules:**
- Maximum function length: 50 lines (extract helpers if longer)
- Maximum file length: 500 lines (split into modules)
- Always use type hints for function parameters and return values
- Use `Optional[Type]` instead of `Type | None` for Python < 3.10
- Add docstrings for all public functions/classes

**Example:**
```python
def get_trial_balance(
    as_of_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TrialBalanceResponse:
    """
    Generate Trial Balance
    
    Shows accounts with their debit and credit balances.
    Only includes POSTED entries (excludes DRAFT and CANCELLED).
    
    Args:
        as_of_date: Date for which to calculate trial balance
        db: Database session
        current_user: Authenticated user
        
    Returns:
        TrialBalanceResponse with account balances
        
    Raises:
        HTTPException: If user doesn't have access
    """
    # Implementation...
```

#### JavaScript/React (Frontend)

**Component Structure:**
```javascript
import React, { useState, useEffect } from 'react';
import { Button, TextField } from '@mui/material';
import api from '../../services/api';

/**
 * Component description
 * @param {Object} props - Component props
 * @param {string} props.entryId - Journal entry ID
 */
function JournalEntryRow({ entry, onPost, onCancel }) {
  // Hooks at the top
  const [loading, setLoading] = useState(false);
  
  // Event handlers
  const handlePost = async () => {
    // Implementation
  };
  
  // Effects
  useEffect(() => {
    // Side effects
  }, [dependencies]);
  
  // Render
  return (
    // JSX
  );
}

export default JournalEntryRow;
```

**Naming Conventions:**
- Components: `PascalCase` (e.g., `JournalEntryRow`)
- Functions: `camelCase` (e.g., `handlePostEntry`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)
- Files: Match component name (e.g., `JournalEntryRow.js`)

**Code Quality Rules:**
- Maximum component length: 200 lines (extract sub-components)
- Use functional components with hooks (no class components)
- Always handle loading and error states
- Use meaningful variable names (avoid `data`, `temp`, `x`)
- Destructure props at function signature

### 2.2 Error Handling

#### Backend (FastAPI)

**Always:**
- Use specific HTTP status codes (400, 401, 403, 404, 500)
- Provide clear error messages
- Log errors with context
- Never expose internal errors to frontend

**Example:**
```python
from app.core.logging import logger

@router.post("/{entry_id}/post")
def post_journal_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        entry = db.query(JournalEntry).filter(
            JournalEntry.id == entry_id,
            JournalEntry.temple_id == current_user.temple_id
        ).first()
        
        if not entry:
            raise HTTPException(
                status_code=404,
                detail="Journal entry not found"
            )
        
        if entry.status != JournalEntryStatus.DRAFT:
            raise HTTPException(
                status_code=400,
                detail=f"Only draft entries can be posted. Current status: {entry.status}"
            )
        
        # Business logic...
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(
            f"Error posting journal entry {entry_id}",
            exc_info=True,
            extra={"entry_id": entry_id, "user_id": current_user.id}
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )
```

#### Frontend (React)

**Always:**
- Handle API errors gracefully
- Show user-friendly error messages
- Log errors to console (development) or error tracking service (production)
- Provide retry mechanisms for transient errors

**Example:**
```javascript
const handlePostEntry = async (entryId) => {
  setLoading(true);
  try {
    await api.post(`/api/v1/journal-entries/${entryId}/post`);
    setSnackbar({
      open: true,
      message: 'Entry posted successfully',
      severity: 'success'
    });
    fetchEntries(); // Refresh list
  } catch (error) {
    console.error('Error posting entry:', error);
    const errorMessage = error.response?.data?.detail 
      || error.message 
      || 'Failed to post entry. Please try again.';
    
    setSnackbar({
      open: true,
      message: errorMessage,
      severity: 'error'
    });
  } finally {
    setLoading(false);
  }
};
```

### 2.3 Database Operations

**Always:**
- Use transactions for multi-step operations
- Handle database errors explicitly
- Use parameterized queries (SQLAlchemy does this automatically)
- Add database constraints (unique, foreign keys, check constraints)
- Never use raw SQL unless absolutely necessary

**Example:**
```python
def cancel_journal_entry(
    entry_id: int,
    cancel_data: JournalEntryCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Start transaction (SQLAlchemy auto-commits on success)
    try:
        entry = db.query(JournalEntry).filter(
            JournalEntry.id == entry_id
        ).first()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        # Mark as cancelled
        entry.status = JournalEntryStatus.CANCELLED
        entry.cancelled_by = current_user.id
        entry.cancelled_at = datetime.utcnow()
        
        # Create reversal entry
        reversal_entry = JournalEntry(...)
        db.add(reversal_entry)
        
        # Create reversal lines
        for line in entry.journal_lines:
            reversed_line = JournalLine(...)
            db.add(reversed_line)
        
        # Commit transaction
        db.commit()
        
        # Refresh objects to get updated data
        db.refresh(entry)
        db.refresh(reversal_entry)
        
        return entry
        
    except Exception as e:
        db.rollback()  # Rollback on error
        logger.error(f"Error cancelling entry {entry_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to cancel entry")
```

### 2.4 State Management

**Frontend State Rules:**
- Keep state as local as possible (use component state)
- Lift state up only when multiple components need it
- Use context API for global state (user, theme, etc.)
- Avoid prop drilling (pass props more than 2 levels)

**Example:**
```javascript
// ❌ Bad: Too much state in one component
function JournalEntries() {
  const [entries, setEntries] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  // ... 10 more state variables
}

// ✅ Good: Extract related state into custom hooks
function useJournalEntries() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const fetchEntries = async () => {
    // Implementation
  };
  
  return { entries, loading, error, fetchEntries };
}

function JournalEntries() {
  const { entries, loading, error, fetchEntries } = useJournalEntries();
  const { accounts } = useAccounts();
  // Clean and focused
}
```

---

## Testing Phase

### 3.1 Testing Strategy

**Test Pyramid:**
```
        /\
       /  \  E2E Tests (Few)
      /____\
     /      \  Integration Tests (Some)
    /________\
   /          \  Unit Tests (Many)
  /____________\
```

### 3.2 Unit Tests

**Backend (pytest):**

**Location:** `backend/tests/unit/`

**Naming:** `test_<module>_<function>.py`

**Example:**
```python
# backend/tests/unit/test_journal_entries.py
import pytest
from datetime import date
from app.api.journal_entries import get_trial_balance
from app.models.accounting import JournalEntryStatus

def test_trial_balance_excludes_cancelled_entries(db_session, test_user):
    """Test that cancelled entries are excluded from trial balance"""
    # Arrange: Create posted entry
    posted_entry = create_test_entry(status=JournalEntryStatus.POSTED)
    
    # Arrange: Create cancelled entry
    cancelled_entry = create_test_entry(status=JournalEntryStatus.CANCELLED)
    
    # Act
    result = get_trial_balance(
        as_of_date=date.today(),
        db=db_session,
        current_user=test_user
    )
    
    # Assert
    assert cancelled_entry.id not in [e.id for e in result.entries]
    assert posted_entry.id in [e.id for e in result.entries]

def test_reversal_entry_uses_same_date(db_session, test_user):
    """Test that reversal entry uses same date as original"""
    # Arrange
    original_date = date(2025, 12, 22)
    original_entry = create_test_entry(
        status=JournalEntryStatus.POSTED,
        entry_date=original_date
    )
    
    # Act
    cancel_journal_entry(
        entry_id=original_entry.id,
        cancel_data={"cancellation_reason": "Test"},
        db=db_session,
        current_user=test_user
    )
    
    # Assert
    reversal = db_session.query(JournalEntry).filter(
        JournalEntry.narration.like("Reversal of%")
    ).first()
    
    assert reversal.entry_date.date() == original_date
```

**Frontend (Jest + React Testing Library):**

**Location:** `frontend/src/__tests__/` or `frontend/src/**/*.test.js`

**Example:**
```javascript
// frontend/src/pages/accounting/__tests__/JournalEntries.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import JournalEntries from '../JournalEntries';
import api from '../../../services/api';

jest.mock('../../../services/api');

describe('JournalEntries', () => {
  beforeEach(() => {
    api.get.mockResolvedValue({
      data: [
        {
          id: 1,
          entry_number: 'JE/2025/0001',
          status: 'DRAFT',
          // ... other fields
        }
      ]
    });
  });

  it('should show Post button for DRAFT entries', async () => {
    render(<JournalEntries />);
    
    await waitFor(() => {
      expect(screen.getByText('Post')).toBeInTheDocument();
    });
  });

  it('should post entry when Post button is clicked', async () => {
    api.post.mockResolvedValue({ data: { id: 1, status: 'POSTED' } });
    
    render(<JournalEntries />);
    
    const postButton = await screen.findByText('Post');
    fireEvent.click(postButton);
    
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/api/v1/journal-entries/1/post');
    });
  });
});
```

### 3.3 Integration Tests

**Backend API Tests:**

**Location:** `backend/tests/integration/`

**Example:**
```python
# backend/tests/integration/test_journal_entries_api.py
import pytest
from fastapi.testclient import TestClient

def test_post_journal_entry_flow(client, auth_headers):
    """Test complete flow: create -> post -> cancel"""
    # Create entry
    response = client.post(
        "/api/v1/journal-entries/",
        json={
            "entry_date": "2025-12-25T00:00:00",
            "narration": "Test entry",
            "journal_lines": [
                {"account_id": 1, "debit_amount": 1000, "credit_amount": 0}
            ]
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    entry_id = response.json()["id"]
    
    # Post entry
    response = client.post(
        f"/api/v1/journal-entries/{entry_id}/post",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "POSTED"
    
    # Cancel entry
    response = client.post(
        f"/api/v1/journal-entries/{entry_id}/cancel",
        json={"cancellation_reason": "Test cancellation"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"
```

### 3.4 Test Requirements

**Before merging any PR:**
- [ ] All existing tests pass
- [ ] New code has unit tests (minimum 70% coverage)
- [ ] Integration tests for new API endpoints
- [ ] Frontend tests for new components/interactions
- [ ] Manual testing checklist completed

**Test Checklist Template:**
```markdown
## Manual Testing Checklist

### Feature: Journal Entry Reversal

- [ ] Create journal entry → Status: DRAFT
- [ ] Post journal entry → Status: POSTED
- [ ] Cancel journal entry → Status: CANCELLED, Reversal created
- [ ] Verify reversal entry has same date as original
- [ ] Verify reversal entry has swapped debits/credits
- [ ] Verify trial balance excludes cancelled entry
- [ ] Verify trial balance includes reversal entry
- [ ] Test error cases (cancel already cancelled entry, etc.)
```

---

## Code Review Process

### 4.1 Pre-Submission Checklist

**Before creating PR:**
- [ ] Code follows style guide (run linters)
- [ ] All tests pass locally
- [ ] No console.log or debug statements
- [ ] No commented-out code
- [ ] Documentation updated (if needed)
- [ ] Migration scripts created (if database changes)

### 4.2 PR Template

**Create `.github/pull_request_template.md`:**

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issue
Closes #<issue_number>

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] Test checklist completed (see below)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->

## Additional Notes
<!-- Any additional information for reviewers -->
```

### 4.3 Review Guidelines

**Reviewers should check:**
1. **Functionality:** Does it work as intended?
2. **Code Quality:** Is it readable, maintainable?
3. **Security:** Any security vulnerabilities?
4. **Performance:** Any performance issues?
5. **Testing:** Are tests adequate?
6. **Documentation:** Is code documented?

**Review Comments:**
- Be constructive and specific
- Suggest solutions, not just problems
- Approve when ready, request changes when needed
- Use "Request Changes" for blocking issues

---

## Deployment Phase

### 5.1 Pre-Deployment Checklist

**Before deploying to production:**
- [ ] All tests pass in CI/CD pipeline
- [ ] Code review approved by at least 1 reviewer
- [ ] Staging environment tested
- [ ] Database migrations tested
- [ ] Rollback plan documented
- [ ] Deployment window scheduled (if needed)
- [ ] Team notified of deployment

### 5.2 Deployment Strategy

**Current Setup (Standalone):**
1. Stop services
2. Backup database
3. Update code
4. Run migrations
5. Start services
6. Verify health endpoints

**Future (Recommended - CI/CD):**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          cd backend && pytest
          cd frontend && npm test
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        # Deployment steps
```

### 5.3 Database Migrations

**Always:**
- Test migrations on staging first
- Backup database before migration
- Make migrations reversible (when possible)
- Document migration steps

**Example:**
```python
# backend/alembic/versions/xxxx_add_reversal_date.py
"""Add reversal_date to journal_entries

Revision ID: xxxx
Revises: yyyy
Create Date: 2025-12-25
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('journal_entries', 
        sa.Column('reversal_date', sa.DateTime(), nullable=True)
    )

def downgrade():
    op.drop_column('journal_entries', 'reversal_date')
```

---

## Post-Deployment Monitoring

### 6.1 Health Checks

**Backend Health Endpoint:**
```python
@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check database connection
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service unhealthy")
```

**Monitor:**
- Response time (< 200ms for health endpoint)
- Error rate (< 1% of requests)
- Database connection pool usage
- Memory/CPU usage

### 6.2 Logging

**Structured Logging:**
```python
import logging
from app.core.logging import logger

# Use structured logging
logger.info(
    "Journal entry posted",
    extra={
        "entry_id": entry.id,
        "entry_number": entry.entry_number,
        "user_id": current_user.id,
        "temple_id": entry.temple_id
    }
)

logger.error(
    "Failed to post journal entry",
    exc_info=True,
    extra={
        "entry_id": entry_id,
        "error": str(e)
    }
)
```

**Log Levels:**
- DEBUG: Detailed information for debugging
- INFO: General informational messages
- WARNING: Warning messages (non-critical issues)
- ERROR: Error messages (handled exceptions)
- CRITICAL: Critical errors (unhandled exceptions)

### 6.3 Error Tracking

**Recommended Tools:**
- Sentry (for both backend and frontend)
- LogRocket (for frontend)
- Custom error tracking dashboard

**Setup Example:**
```python
# backend/app/core/error_tracking.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% of transactions
    environment=os.getenv("ENVIRONMENT", "development")
)
```

---

## Incident Response

### 7.1 Incident Severity Levels

**P0 - Critical:**
- Production system down
- Data loss/corruption
- Security breach
- Response: Immediate (within 15 minutes)

**P1 - High:**
- Major feature broken
- Performance degradation (>50% slower)
- Response: Within 1 hour

**P2 - Medium:**
- Minor feature broken
- UI issues
- Response: Within 4 hours

**P3 - Low:**
- Cosmetic issues
- Documentation errors
- Response: Next business day

### 7.2 Incident Response Process

1. **Detect:** Monitor alerts, user reports
2. **Assess:** Determine severity, impact
3. **Communicate:** Notify team, stakeholders
4. **Mitigate:** Apply quick fix or rollback
5. **Resolve:** Implement proper fix
6. **Post-Mortem:** Document root cause, prevention

### 7.3 Rollback Procedure

**Quick Rollback Steps:**
```bash
# 1. Stop services
# 2. Restore previous code version
git checkout <previous-commit-hash>

# 3. Restore database (if needed)
# Use backup from before deployment

# 4. Start services
# 5. Verify health
curl http://localhost:8000/health
```

**Rollback Decision Matrix:**
- If error rate > 10% → Rollback immediately
- If critical feature broken → Rollback
- If data integrity at risk → Rollback
- If fix available < 30 minutes → Fix forward
- If fix available > 30 minutes → Rollback

### 7.4 Post-Mortem Template

```markdown
# Post-Mortem: [Incident Title]

## Incident Summary
- Date: YYYY-MM-DD
- Duration: X hours
- Impact: [Description]
- Severity: P0/P1/P2/P3

## Timeline
- HH:MM: Issue detected
- HH:MM: Team notified
- HH:MM: Mitigation applied
- HH:MM: Issue resolved

## Root Cause
[Detailed analysis of what went wrong]

## Impact
- Users affected: X
- Features affected: [List]
- Data affected: [If any]

## Resolution
[What was done to fix it]

## Prevention
- [ ] Action item 1
- [ ] Action item 2
- [ ] Action item 3

## Lessons Learned
[Key takeaways]
```

---

## Tools & Configuration

### 8.1 Required Tools

**Backend:**
- `black` - Code formatter
- `flake8` or `pylint` - Linter
- `mypy` - Type checker
- `pytest` - Testing framework
- `pytest-cov` - Coverage tool

**Frontend:**
- `eslint` - Linter
- `prettier` - Code formatter
- `jest` - Testing framework
- `@testing-library/react` - Component testing

### 8.2 Configuration Files

**Create these files:**

**`.pre-commit-config.yaml`** (Root directory):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.12
        files: ^backend/

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        files: ^backend/

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.42.0
    hooks:
      - id: eslint
        files: ^frontend/
        additional_dependencies:
          - eslint@8.42.0
```

**`backend/pyproject.toml`**:
```toml
[tool.black]
line-length = 100
target-version = ['py312']
include = '\.pyi?$'

[tool.flake8]
max-line-length = 100
exclude = [".git", "__pycache__", "venv", "migrations"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=app --cov-report=html --cov-report=term"
```

**`frontend/.eslintrc.js`**:
```javascript
module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
  ],
  parserOptions: {
    ecmaVersion: 2021,
    sourceType: 'module',
  },
  rules: {
    'no-console': 'warn',
    'no-unused-vars': 'error',
    'react/prop-types': 'off', // If using TypeScript
  },
};
```

### 8.3 Git Workflow

**Branch Strategy:**
- `main` - Production code (protected)
- `develop` - Development branch
- `feature/<name>` - Feature branches
- `bugfix/<name>` - Bug fix branches
- `hotfix/<name>` - Urgent production fixes

**Commit Messages:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example:**
```
fix(accounting): Exclude cancelled entries from trial balance

- Updated get_trial_balance to filter out CANCELLED status
- Fixed reversal entry date to match original entry
- Added unit tests for cancellation flow

Fixes #123
```

---

## Quick Reference Checklist

### Before Writing Code
- [ ] Issue/feature request created
- [ ] Design reviewed (if complex)
- [ ] Impact analysis completed

### While Writing Code
- [ ] Follows coding standards
- [ ] Type hints added (Python)
- [ ] Error handling implemented
- [ ] Logging added for important operations
- [ ] Comments added for complex logic

### Before Committing
- [ ] Code formatted (black/prettier)
- [ ] Linter passes
- [ ] Tests written and passing
- [ ] No debug code left

### Before PR
- [ ] All tests pass
- [ ] Manual testing completed
- [ ] Documentation updated
- [ ] PR description filled

### Before Deployment
- [ ] Code review approved
- [ ] Staging tested
- [ ] Database migrations tested
- [ ] Rollback plan ready
- [ ] Team notified

### After Deployment
- [ ] Health checks passing
- [ ] Monitoring alerts configured
- [ ] Error rates normal
- [ ] User feedback positive

---

## Implementation Priority

**Phase 1 (Immediate - This Week):**
1. Set up pre-commit hooks
2. Configure linters (flake8, eslint)
3. Create PR template
4. Set up basic logging

**Phase 2 (Short-term - This Month):**
1. Add unit tests for critical paths
2. Set up CI/CD pipeline
3. Configure error tracking (Sentry)
4. Create deployment checklist

**Phase 3 (Long-term - Next Quarter):**
1. Achieve 80%+ test coverage
2. Set up staging environment
3. Implement automated monitoring
4. Create incident response playbook

---

## Review & Updates

**This SOP should be:**
- Reviewed quarterly
- Updated after major incidents
- Shared with all team members
- Referenced in onboarding

**Last Review Date:** 2025-12-25  
**Next Review Date:** 2026-03-25  
**Owner:** Development Team

---

## Questions or Suggestions?

If you have questions or suggestions for improving this SOP, please:
1. Create an issue in the repository
2. Discuss in team meetings
3. Update this document with improvements

**Remember:** The goal is not perfection, but continuous improvement. Start with what's feasible and build from there.


