# 🚀 Getting Started with MandirSync

**Complete guide to get your development environment ready**

---

## ⚡ Quick Setup (15 minutes)

### Step 1: Install Prerequisites

Make sure you have these installed:

- ✅ **Python 3.11+** - [Download](https://www.python.org/downloads/)
- ✅ **Node.js 18+** - [Download](https://nodejs.org/)
- ✅ **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/windows/)
- ✅ **Git** - [Download](https://git-scm.com/download/win)
- ✅ **VS Code** (recommended) - [Download](https://code.visualstudio.com/)

**Detailed installation instructions**: See [scripts/setup_windows.md](scripts/setup_windows.md)

---

### Step 2: Setup Database

Open **Command Prompt** or **PowerShell**:

```powershell
# Connect to PostgreSQL
psql -U postgres

# Enter your PostgreSQL password

# Create database
CREATE DATABASE temple_db;

# Verify
\l

# Exit
\q
```

---

### Step 3: Setup Backend

```powershell
# Navigate to project
cd D:\MandirSync\backend

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# You should see (venv) in your prompt

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Edit .env with your database password
notepad .env
```

**In .env file, update this line:**
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/temple_db
```

Replace `YOUR_PASSWORD` with your PostgreSQL password.

---

### Step 4: Run Backend

```powershell
# Make sure you're in backend folder with (venv) active
python app/main.py
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

### Step 5: Test API

Open your browser and visit:

- **API Info**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Interactive!)
- **Health Check**: http://localhost:8000/health

**If you see the API documentation page, congratulations! 🎉**

Press `Ctrl+C` in terminal to stop the server.

---

## 📁 What's Been Created

Your project now has:

```
MandirSync/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py        ✅ Configuration system
│   │   │   ├── database.py      ✅ Database connection
│   │   │   └── security.py      ✅ Auth utilities
│   │   ├── models/
│   │   │   ├── temple.py        ✅ Temple model
│   │   │   ├── user.py          ✅ User model
│   │   │   ├── devotee.py       ✅ Devotee model
│   │   │   └── donation.py      ✅ Donation models
│   │   └── main.py              ✅ FastAPI app
│   ├── .env                     ✅ Your config
│   ├── .env.example             ✅ Template
│   ├── requirements.txt         ✅ Dependencies
│   └── venv/                    ✅ Virtual environment
├── docs/                        ✅ Documentation
└── scripts/                     ✅ Setup guides
```

---

## 🎯 Next Steps - Build Donation Module!

Now that setup is complete, let's build our first feature: **Donation Management**

### What We'll Build:

1. **Pydantic Schemas** - Data validation
2. **API Endpoints** - Create, list, get donations
3. **Service Layer** - Business logic
4. **Reports** - Daily collection summary

### Files We'll Create:

```
backend/app/
├── schemas/
│   ├── __init__.py
│   ├── donation.py         ← Validation schemas
│   └── devotee.py
├── services/
│   ├── __init__.py
│   ├── donation_service.py ← Business logic
│   └── devotee_service.py
└── api/
    ├── __init__.py
    ├── auth.py             ← Authentication
    ├── donations.py        ← Donation endpoints
    └── devotees.py
```

---

## 📚 Learning Resources

If you're new to any of these technologies:

### FastAPI (Recommended!)
- 📖 [Official Tutorial](https://fastapi.tiangolo.com/tutorial/)
- 🎥 [FastAPI in 45 minutes](https://www.youtube.com/watch?v=0sOvCWFmrtA)

### SQLAlchemy
- 📖 [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- 🎥 [SQLAlchemy Basics](https://www.youtube.com/watch?v=AKQ3XEDI9Mw)

### Pydantic
- 📖 [Pydantic Docs](https://docs.pydantic.dev/)

---

## 🐛 Troubleshooting

### "python is not recognized"

**Fix**: Python not in PATH
- Add Python to system PATH
- Reinstall Python with "Add to PATH" checked

### "psql is not recognized"

**Fix**: PostgreSQL not in PATH
- Add `C:\Program Files\PostgreSQL\14\bin` to PATH

### Cannot connect to database

**Fix**: Check PostgreSQL service
1. Open Services (Win+R, type `services.msc`)
2. Find "postgresql-x64-14"
3. Make sure it's "Running"

### Port 8000 already in use

**Fix**: Change port in `.env`:
```
PORT=8001
```

### Module not found error

**Fix**: Activate virtual environment
```powershell
cd backend
venv\Scripts\activate
```

---

## 💡 Development Tips

### 1. Keep Virtual Environment Active

Always work with `(venv)` showing in your prompt:
```powershell
cd D:\MandirSync\backend
venv\Scripts\activate
```

### 2. Use API Documentation

The interactive docs at http://localhost:8000/docs are your best friend:
- Test endpoints directly
- See request/response formats
- Try out authentication

### 3. Check Logs

If something doesn't work, check the terminal where the server is running. FastAPI gives detailed error messages.

### 4. Database GUI

Use a database GUI to see your data:
- **pgAdmin** (comes with PostgreSQL)
- **DBeaver** (my favorite) - https://dbeaver.io/

---

## ✅ Checklist

Before moving forward, make sure:

- [ ] Python 3.11+ installed and working
- [ ] PostgreSQL 14+ installed and running
- [ ] Database `temple_db` created
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with correct database URL
- [ ] Backend server runs successfully
- [ ] Can access http://localhost:8000/docs

**All checked? Awesome! You're ready to build! 🎉**

---

## 🚀 Ready for Next Step?

**What to do next:**

1. **Want to build authentication first?**
   - I'll create login/register endpoints
   - User management

2. **Want to jump into donations?**
   - Create donation API
   - Build donation forms

3. **Want to learn more about the codebase?**
   - I'll explain each file
   - Show how everything connects

Just let me know and I'll guide you step-by-step! 💪

---

## 📞 Need Help?

- **Documentation Error?** Let me know, I'll fix it
- **Setup Issue?** Share the error message
- **Concept Unclear?** Ask for explanation
- **Want to Try Something?** I'll help you experiment

**Remember: No question is too basic! We're here to learn and build together.** 🙌

---

**Current Status**: ✅ Development environment ready!  
**Next**: Build your first feature (Donation Management)  
**Time to build**: ~2 hours for basic donation API

**Let's code!** 🚀


