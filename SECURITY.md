# Security Policy — MandirMitra

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.x     | ✅ Active support  |
| < 1.0   | ❌ Not supported   |

## Reporting a Vulnerability

MandirMitra handles temple finances and personal devotee data.
We take security vulnerabilities extremely seriously.

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Instead, report them privately:

1. **Email:** security@mandirmitra.in  
   _Subject line:_ `[SECURITY] Brief description`
2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Your suggested fix (optional)

We will acknowledge within **48 hours** and aim to patch within **7 days** for critical issues.

## Security Measures in Place

- 🔐 JWT authentication with short-lived access tokens (2 hrs)
- 🔒 bcrypt password hashing (Argon2 upgrade planned)
- 🛡️ Role-Based Access Control (Admin, Accountant, Priest, Viewer, Data Entry)
- 🔑 Fernet encryption for sensitive data fields
- 📋 Audit logging on all financial operations
- 🚦 Rate limiting on all API endpoints (stricter on auth endpoints)
- 🔏 Account lockout after repeated failed login attempts
- 🌐 CORS locked to specific origin domains in production
- 🔒 HTTPS enforced in production (HSTS enabled)
- 🧪 Bandit + pip-audit security scanning in CI/CD pipeline
- 🗄️ Database tamper-detection / integrity hash checks
- 📦 Non-root Docker container user in production

## Responsible Disclosure

We follow responsible disclosure practices.
Security researchers who report valid vulnerabilities will be credited in our CHANGELOG.
