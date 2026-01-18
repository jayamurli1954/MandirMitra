# Windows 11 Setup Guide for MandirSync

Complete step-by-step guide for setting up the development environment on Windows 11.

## Prerequisites Installation

### Step 1: Install Python 3.11

1. Go to https://www.python.org/downloads/
2. Download **Python 3.11.x**
3. Run installer
   - ☑ **Check "Add Python to PATH"**
   - ☑ Check "Install for all users"
   - Click "Install Now"
4. Verify installation:
   ```powershell
   python --version
   # Should show: Python 3.11.x
   
   pip --version
   # Should show: pip 23.x
   ```

### Step 2: Install Node.js 18

1. Go to https://nodejs.org/
2. Download **18.x LTS** (Recommended)
3. Run installer with default settings
4. Verify installation:
   ```powershell
   node --version
   # Should show: v18.x.x
   
   npm --version
   # Should show: 9.x.x
   ```

### Step 3: Install PostgreSQL 14+

1. Go to https://www.postgresql.org/download/windows/
2. Download **PostgreSQL 14** (or higher)
3. Run installer:
   - **Password**: Choose and remember it (e.g., `postgres123`)
   - **Port**: 5432 (default)
   - **Locale**: Default
   - **Stack Builder**: Uncheck (not needed)
4. Add to PATH (if not automatic):
   - Open "Edit system environment variables"
   - Click "Environment Variables"
   - Edit "Path" under "System variables"
   - Add: `C:\Program Files\PostgreSQL\14\bin`
5. Verify installation:
   ```powershell
   psql --version
   # Should show: psql (PostgreSQL) 14.x
   ```

### Step 4: Install Git

1. Go to https://git-scm.com/download/win
2. Download Git for Windows
3. Run installer with defaults
4. Verify installation:
   ```powershell
   git --version
   # Should show: git version 2.x.x
   ```

### Step 5: Install VS Code (Recommended)

1. Go to https://code.visualstudio.com/
2. Download and install
3. Install recommended extensions:
   - Python (by Microsoft)
   - Pylance
   - Python Debugger
   - ESLint
   - Prettier - Code formatter
   - PostgreSQL (by Chris Kolkman)

---

## Project Setup

### Step 1: Create Database

Open Command Prompt or PowerShell:

```powershell
# Start PostgreSQL command line
psql -U postgres

# Enter your PostgreSQL password when prompted

# Create database
CREATE DATABASE temple_db;

# Create user (optional, or use postgres user)
CREATE USER temple_user WITH PASSWORD 'temple_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE temple_db TO temple_user;

# Exit
\q
```

### Step 2: Clone/Setup Project

```powershell
# Navigate to where you want the project
cd D:\

# Create project directory
mkdir MandirSync
cd MandirSync

# Initialize Git
git init
git branch -M main

# Create folder structure
mkdir backend frontend docs scripts
```

### Step 3: Setup Backend

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
# You should see (venv) in your prompt

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic pydantic pydantic-settings python-dotenv
pip install python-multipart aiofiles python-jose passlib bcrypt
pip install pytest pytest-cov httpx

# Save dependencies
pip freeze > requirements.txt

# Copy .env.example to .env
copy .env.example .env

# Edit .env file
notepad .env
```

Update the `.env` file with your PostgreSQL password:
```
DATABASE_URL=postgresql://postgres:your_password_here@localhost:5432/temple_db
```

### Step 4: Test Backend

```powershell
# Make sure you're in backend folder with venv activated
python app/main.py

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

Open browser and go to:
- http://localhost:8000 - Should show API info
- http://localhost:8000/docs - Should show interactive API documentation

Press `Ctrl+C` to stop the server.

### Step 5: Setup Frontend (Later)

```powershell
# Navigate to frontend folder
cd ..\frontend

# Create React app
npx create-react-app . --template typescript

# Install dependencies
npm install @mui/material @emotion/react @emotion/styled
npm install axios react-router-dom
npm install @mui/icons-material

# Start frontend
npm start
```

---

## Common Issues and Solutions

### Issue 1: "python is not recognized"

**Solution**: Python not in PATH.
1. Find Python installation path (usually `C:\Users\YourName\AppData\Local\Programs\Python\Python311`)
2. Add to PATH:
   - Right-click "This PC" → Properties
   - Advanced system settings → Environment Variables
   - Edit "Path" → Add Python path

### Issue 2: "psql is not recognized"

**Solution**: PostgreSQL not in PATH.
1. Add to PATH: `C:\Program Files\PostgreSQL\14\bin`

### Issue 3: Cannot connect to database

**Error**: `could not connect to server`

**Solution**:
1. Check PostgreSQL is running:
   - Open Services (services.msc)
   - Look for "postgresql-x64-14"
   - Make sure it's running
2. Check password in .env is correct
3. Check database exists:
   ```powershell
   psql -U postgres -l
   ```

### Issue 4: Port 8000 already in use

**Error**: `[Errno 10048]`

**Solution**: Change port in .env:
```
PORT=8001
```

### Issue 5: Module not found

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
1. Make sure virtual environment is activated (you should see `(venv)` in prompt)
2. Run from backend folder: `python -m uvicorn app.main:app --reload`

---

## Next Steps

After setup is complete:

1. ✅ Backend is running
2. ✅ Database is connected
3. ✅ API docs accessible

**Now you're ready to build features!**

Next steps:
1. Create authentication system
2. Build donation management API
3. Create frontend UI
4. Test end-to-end

---

## Quick Reference Commands

```powershell
# Activate virtual environment
cd D:\MandirSync\backend
venv\Scripts\activate

# Run backend server
python app/main.py

# Or with uvicorn
uvicorn app.main:app --reload

# Run frontend (in separate terminal)
cd D:\MandirSync\frontend
npm start

# Check database
psql -U postgres -d temple_db

# Run tests
pytest

# Install new package
pip install package_name
pip freeze > requirements.txt
```

---

## Useful Links

- FastAPI Docs: https://fastapi.tiangolo.com/
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
- React Docs: https://react.dev/
- Material-UI: https://mui.com/
- PostgreSQL Docs: https://www.postgresql.org/docs/

---

**You're all set! Time to build MandirSync!** 🚀


