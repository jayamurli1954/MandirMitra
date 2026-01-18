# Contributing to MandirMitra - Temple Management System

First off, thank you for considering contributing to MandirMitra - Temple Management System! It's people like you that make this project a great tool for temples across India.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

### Our Pledge

We are committed to providing a friendly, safe, and welcoming environment for all, regardless of level of experience, gender identity, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

### Expected Behavior

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When you create a bug report, include as many details as possible:

**Bug Report Template:**
```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Ubuntu 22.04]
 - Browser: [e.g. Chrome 120]
 - Python Version: [e.g. 3.11]
 - Database: [e.g. PostgreSQL 14]

**Additional context**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any alternatives** you've considered

### Your First Code Contribution

Unsure where to begin? Start by looking through `good-first-issue` and `help-wanted` issues:

- **good-first-issue** - Issues suitable for beginners
- **help-wanted** - Issues that need attention

### Pull Requests

- Fill in the required template
- Follow the coding standards
- Include tests for new features
- Update documentation
- End all files with a newline

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Git
- Docker (optional but recommended)

### Setting Up Development Environment

1. **Fork the repository**
   ```bash
   # Visit https://github.com/yourusername/temple-management
   # Click "Fork" button
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/temple-management.git
   cd temple-management
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/original-owner/temple-management.git
   ```

4. **Set up backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Dev dependencies
   
   # Set up database
   createdb temple_db_dev
   
   # Copy environment file
   cp .env.example .env
   # Edit .env with your settings
   
   # Run migrations
   alembic upgrade head
   
   # Run tests to verify setup
   pytest
   ```

5. **Set up frontend**
   ```bash
   cd ../frontend
   npm install
   
   # Copy environment file
   cp .env.example .env
   # Edit .env
   
   # Run tests
   npm test
   ```

6. **Start development servers**
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn app.main:app --reload
   
   # Terminal 2: Frontend
   cd frontend
   npm start
   ```

---

## Development Workflow

### Branch Strategy

We use Git Flow:

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes

### Workflow Steps

1. **Sync with upstream**
   ```bash
   git checkout develop
   git fetch upstream
   git merge upstream/develop
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/seva-booking
   ```

3. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

4. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   pytest
   pytest --cov=app --cov-report=html
   
   # Frontend tests
   cd frontend
   npm test
   npm run lint
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add seva booking functionality"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/seva-booking
   ```

7. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Fill in the template
   - Submit!

---

## Coding Standards

### Python (Backend)

**Style Guide:** PEP 8

**Formatting:**
```bash
# Format with black
black app/

# Check with ruff
ruff check app/

# Type check with mypy
mypy app/
```

**Code Style:**
```python
# Good
def create_donation(
    devotee_id: int,
    amount: float,
    category: str
) -> Donation:
    """
    Create a new donation record.
    
    Args:
        devotee_id: ID of the devotee
        amount: Donation amount in rupees
        category: Donation category name
        
    Returns:
        Created donation object
        
    Raises:
        ValueError: If amount is negative
    """
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    donation = Donation(
        devotee_id=devotee_id,
        amount=amount,
        category=category
    )
    db.session.add(donation)
    db.session.commit()
    
    return donation
```

**Testing:**
```python
# test_donations.py
import pytest
from app.services.donation_service import DonationService

def test_create_donation():
    """Test creating a donation."""
    service = DonationService()
    
    donation = service.create_donation(
        devotee_id=1,
        amount=1000,
        category="General"
    )
    
    assert donation.id is not None
    assert donation.amount == 1000
    assert donation.category == "General"

def test_create_donation_negative_amount():
    """Test creating donation with negative amount raises error."""
    service = DonationService()
    
    with pytest.raises(ValueError):
        service.create_donation(
            devotee_id=1,
            amount=-100,
            category="General"
        )
```

### JavaScript/React (Frontend)

**Style Guide:** Airbnb JavaScript Style Guide

**Formatting:**
```bash
# Format with prettier
npm run format

# Lint with eslint
npm run lint
npm run lint:fix
```

**Code Style:**
```javascript
// Good
import React, { useState, useEffect } from 'react';
import { Box, Button, TextField } from '@mui/material';
import { donationService } from '../services/donationService';

/**
 * Donation form component
 * Allows recording of new donations
 */
const DonationForm = () => {
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await donationService.create({ amount });
      // Handle success
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <TextField
        label="Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        type="number"
        required
      />
      <Button type="submit" disabled={loading}>
        {loading ? 'Submitting...' : 'Submit'}
      </Button>
      {error && <div>{error}</div>}
    </Box>
  );
};

export default DonationForm;
```

### Database

**Migration Naming:**
```bash
# Good
alembic revision -m "add_seva_booking_table"
alembic revision -m "add_index_to_donations_date"

# Bad
alembic revision -m "changes"
alembic revision -m "update"
```

**SQL Style:**
```sql
-- Good
SELECT
    d.id,
    d.full_name,
    d.phone,
    SUM(don.amount) as total_donations
FROM devotees d
LEFT JOIN donations don ON d.id = don.devotee_id
WHERE d.temple_id = 1
    AND don.is_cancelled = FALSE
GROUP BY d.id, d.full_name, d.phone
ORDER BY total_donations DESC
LIMIT 10;
```

---

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/).

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semi-colons, etc)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **build**: Build system changes
- **ci**: CI configuration changes
- **chore**: Other changes that don't modify src or test files

### Examples

```bash
# Feature
git commit -m "feat(donations): add recurring donation support"

# Bug fix
git commit -m "fix(bookings): prevent double-booking of sevas"

# Documentation
git commit -m "docs(api): update donation endpoint documentation"

# Breaking change
git commit -m "feat(auth)!: change JWT expiry to 2 hours

BREAKING CHANGE: JWT tokens now expire after 2 hours instead of 24 hours.
Users will need to re-login more frequently."
```

---

## Pull Request Process

### Before Submitting

1. **Update documentation** - If you changed API, update docs
2. **Add tests** - New features must have tests
3. **Run tests** - Ensure all tests pass
4. **Run linters** - Code must pass linting
5. **Update CHANGELOG.md** - Document your changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran

## Checklist:
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published
```

### Review Process

1. **Automated checks** - CI will run tests and linters
2. **Code review** - At least one maintainer must approve
3. **Address feedback** - Make requested changes
4. **Approval** - Once approved, maintainer will merge

### After Merge

- Delete your feature branch
- Update your local develop branch
- Start on next feature!

---

## Release Process

Releases are handled by maintainers:

1. **Version bump** - Update version in package.json, __init__.py
2. **Update CHANGELOG** - Summarize changes
3. **Create release** - Tag and publish on GitHub
4. **Deploy** - Deploy to production

---

## Questions?

- **Documentation:** Check [docs](docs/) folder
- **Issues:** [GitHub Issues](https://github.com/yourusername/temple-management/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/temple-management/discussions)
- **Email:** dev@mandirconnect.com

---

**Thank you for contributing! 🙏**

Together, we're building something that will help temples across India serve devotees better!
