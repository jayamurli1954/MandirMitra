# MandirMitra - Environment Configuration Guide

## Table of Contents

1. [Python Virtual Environment](#python-virtual-environment)
2. [Environment Variables (.env file)](#environment-variables-env-file)
3. [Development vs Production](#development-vs-production)
4. [Quick Reference](#quick-reference)

---

## Python Virtual Environment

### Activating Virtual Environment

**Windows (PowerShell):**
```powershell
cd D:\MandirMitra\backend
venv\Scripts\activate
```

**Windows (Command Prompt):**
```cmd
cd D:\MandirMitra\backend
venv\Scripts\activate.bat
```

**After activation, you'll see:**
```
(venv) PS D:\MandirMitra\backend>
```

### Deactivating Virtual Environment

```powershell
deactivate
```

### Creating New Virtual Environment

If you need to create a fresh virtual environment:

```powershell
# Remove old venv (optional)
Remove-Item -Recurse -Force venv

# Create new virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Switching Between Environments

If you have multiple Python environments (e.g., Anaconda, system Python):

**Option 1: Use specific Python**
```powershell
# Use system Python
python -m venv venv

# Use Anaconda Python
C:\Users\YourName\anaconda3\python.exe -m venv venv
```

**Option 2: Use Anaconda environment**
```powershell
# Create conda environment
conda create -n MandirMitra python=3.11
conda activate MandirMitra

# Install dependencies
pip install -r requirements.txt
```

---

## Environment Variables (.env file)

### Creating .env File

**Step 1: Check if .env exists**
```powershell
cd D:\MandirMitra\backend
dir .env
```

**Step 2: Create .env file (if it doesn't exist)**
```powershell
# Copy from example (if available)
copy .env.example .env

# Or create new file
New-Item -ItemType File -Name .env
```

**Step 3: Edit .env file**
```powershell
# Open in notepad
notepad .env

# Or use VS Code
code .env
```

### .env File Template

Create a `.env` file in `backend/` directory with:

```env
# ============================================
# MandirMitra Backend Configuration
# ============================================

# Deployment Mode
DEPLOYMENT_MODE=standalone

# Database Configuration
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/temple_db

# Security Keys (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS (Frontend URLs)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Database Logging (set to True for debugging SQL queries)
SQL_ECHO=False

# Optional: Email Configuration
EMAIL_ENABLED=False
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com

# Optional: SMS Configuration
SMS_ENABLED=False
SMS_PROVIDER=MSG91
SMS_API_KEY=your-sms-api-key
SMS_SENDER_ID=MANDIR

# Optional: Payment Gateway
PAYMENT_ENABLED=False
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret

# Optional: Encryption (for production)
ENCRYPTION_KEY=your-encryption-key-32-chars-long
```

### Common Environment Variable Changes

#### 1. Change Database Password

```env
# Old
DATABASE_URL=postgresql://postgres:oldpassword@localhost:5432/temple_db

# New
DATABASE_URL=postgresql://postgres:newpassword@localhost:5432/temple_db
```

#### 2. Change Server Port

```env
# Old
PORT=8000

# New
PORT=8080
```

#### 3. Enable Debug Mode

```env
# Development
DEBUG=True
SQL_ECHO=True

# Production
DEBUG=False
SQL_ECHO=False
```

#### 4. Change CORS Origins (for different frontend URL)

```env
# Local development
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### 5. Switch to Production Mode

```env
# Development
DEPLOYMENT_MODE=standalone
DEBUG=True
FORCE_HTTPS=False

# Production
DEPLOYMENT_MODE=standalone
DEBUG=False
FORCE_HTTPS=True
```

### Reloading Environment Variables

After changing `.env` file:

1. **Stop the server** (Ctrl+C)
2. **Restart the server:**
   ```powershell
   python -m uvicorn app.main:app --reload
   ```

The server will automatically reload and pick up new environment variables.

---

## Development vs Production

### Development Environment

**Settings:**
```env
DEBUG=True
SQL_ECHO=True
DEPLOYMENT_MODE=standalone
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000
```

**Features:**
- ✅ Hot reload enabled
- ✅ Detailed error messages
- ✅ SQL query logging
- ✅ CORS allows localhost

### Production Environment

**Settings:**
```env
DEBUG=False
SQL_ECHO=False
DEPLOYMENT_MODE=standalone
HOST=0.0.0.0
PORT=8000
FORCE_HTTPS=True
ALLOWED_ORIGINS=https://yourdomain.com
SECRET_KEY=strong-random-secret-key-here
JWT_SECRET_KEY=strong-random-jwt-secret-key-here
```

**Features:**
- ❌ No hot reload
- ❌ Minimal error messages
- ❌ No SQL logging
- ✅ HTTPS enforced
- ✅ Strong security keys

---

## Quick Reference

### Check Current Environment

**Check Python version:**
```powershell
python --version
```

**Check if venv is active:**
```powershell
# If active, you'll see (venv) in prompt
# Or check:
echo $env:VIRTUAL_ENV
```

**Check installed packages:**
```powershell
pip list
```

**Check environment variables:**
```powershell
# In Python
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

### Common Commands

**Activate environment:**
```powershell
cd D:\MandirMitra\backend
venv\Scripts\activate
```

**Deactivate environment:**
```powershell
deactivate
```

**Edit .env file:**
```powershell
notepad .env
```

**View .env file:**
```powershell
Get-Content .env
```

**Check if .env exists:**
```powershell
Test-Path .env
```

**Create .env from template:**
```powershell
# If .env.example exists
copy .env.example .env

# Or create manually
@"
DATABASE_URL=postgresql://postgres:password@localhost:5432/temple_db
SECRET_KEY=your-secret-key
"@ | Out-File -FilePath .env -Encoding utf8
```

---

## Troubleshooting

### Problem: "Module not found" after activating venv

**Solution:**
```powershell
# Make sure you're in backend directory
cd D:\MandirMitra\backend

# Activate venv
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: Environment variables not loading

**Solution:**
1. Check `.env` file exists in `backend/` directory
2. Check file format (no spaces around `=`)
3. Restart the server
4. Check for typos in variable names

### Problem: Wrong Python version

**Solution:**
```powershell
# Check current Python
python --version

# Create venv with specific Python
C:\Python311\python.exe -m venv venv
```

### Problem: Can't activate venv

**Solution:**
```powershell
# Check if venv exists
Test-Path venv\Scripts\activate.ps1

# If not, create new venv
python -m venv venv

# If PowerShell execution policy blocks, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Best Practices

1. **Never commit .env file** - Add to `.gitignore`
2. **Use different .env files** - `.env.development`, `.env.production`
3. **Change default secrets** - Always change SECRET_KEY and JWT_SECRET_KEY
4. **Use strong passwords** - For database and secrets
5. **Keep .env.example** - Template for other developers
6. **Document changes** - Note what environment variables do

---

**Last Updated:** 28th November 2025


