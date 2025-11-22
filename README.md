# 🛕 MandirSync - Temple Management System

**Comprehensive Temple Administration & Devotee Services Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

---

## 📖 About

MandirSync is a modern temple management system designed specifically for Indian temples. It digitizes and streamlines temple operations including donations, seva bookings, devotee management, accounting, and more.

### Available in Two Modes:

1. **Standalone Version** 🖥️ - Install on temple's own hardware, works offline
2. **SaaS Version** ☁️ - Cloud-based, accessible from anywhere

---

## 🚀 Quick Start

### For Windows 11 Users (You!)

1. **Install Prerequisites**
   - Python 3.11+
   - Node.js 18+
   - PostgreSQL 14+
   - Git

   📝 **Detailed guide**: See [scripts/setup_windows.md](scripts/setup_windows.md)

2. **Setup Database**
   ```powershell
   psql -U postgres
   CREATE DATABASE temple_db;
   \q
   ```

3. **Setup Backend**
   ```powershell
   cd backend
python -m venv venv
   venv\Scripts\activate
pip install -r requirements.txt
   copy .env.example .env
   # Edit .env with your database password
   python app/main.py
   ```

4. **Access API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

---

## 📁 Project Structure

```
MandirSync/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── core/           # Configuration, database, security
│   │   ├── models/         # Database models
│   │   ├── api/            # API endpoints (to be built)
│   │   ├── services/       # Business logic (to be built)
│   │   └── main.py         # FastAPI app
│   ├── tests/              # Backend tests
│   ├── .env.example        # Environment template
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React frontend (to be built)
│   └── (To be created)
│
├── mobile/                 # Flutter mobile app (future)
│   └── (To be created)
│
├── docs/                   # Documentation
│   ├── PRD.md             # Product Requirements
│   ├── ARCHITECTURE.md     # Technical Architecture
│   ├── DATABASE_SCHEMA.md  # Database Design
│   ├── CURSOR_GUIDE.md     # AI Development Guide
│   └── CONTRIBUTING.md     # Contribution Guide
│
├── scripts/                # Utility scripts
│   └── setup_windows.md    # Windows setup guide
│
└── README.md              # This file
```

---

## ✨ Features

### Phase 1: MVP (Current Focus - Weeks 1-8)

- ✅ User Authentication & Authorization
- 🚧 **Donation Management** (In Progress)
  - Quick donation entry
  - Multiple payment modes
  - Automatic receipt generation
  - Devotee auto-suggest
- 📋 Seva/Pooja Booking
- 👥 Devotee CRM
- 📊 Reports & Analytics

### Phase 2: Advanced (Weeks 9-14)

- Complete Accounting System
- Inventory Management
- Asset Management
- Hundi Management

### Phase 3: Premium (Weeks 15+)

- Mobile App (Android/iOS)
- SMS/Email Notifications
- Payment Gateway Integration
- Advanced Analytics

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0+
- **Auth**: JWT (python-jose)

### Frontend (To be built)
- **Framework**: React 18+
- **UI Library**: Material-UI v5
- **State**: Zustand / Redux Toolkit
- **HTTP**: Axios

### Desktop (To be built)
- **Framework**: Electron
- **Target**: Windows, macOS, Linux

### Mobile (Future)
- **Framework**: Flutter
- **Target**: Android, iOS

---

## 📚 Documentation

- **[Product Requirements](PRD.md)** - Complete feature specifications
- **[Technical Architecture](ARCHITECTURE.md)** - System design and tech stack
- **[Database Schema](DATABASE_SCHEMA.md)** - Database structure
- **[Windows Setup Guide](scripts/setup_windows.md)** - Detailed setup for Windows 11
- **[Cursor AI Guide](CURSOR_GUIDE.md)** - Using AI for development
- **[Contributing](CONTRIBUTING.md)** - How to contribute
- **[Conversation Log](CONVERSATION_LOG.md)** - 📝 **Project context & conversation history**
- **[UI Decisions](UI_DECISIONS.md)** - UI/UX design decisions and guidelines
- **[Quick Start](QUICK_START.md)** - Quick context for new conversations

---

## 🎯 Development Roadmap

### ✅ Completed
- [x] Project structure setup
- [x] Database models (Temple, User, Devotee, Donation)
- [x] Configuration system
- [x] Security utilities (password hashing, JWT)
- [x] Database connection

### 🚧 In Progress
- [ ] Donation API endpoints
- [ ] Authentication API
- [ ] Pydantic schemas

### 📋 Next Up
- [ ] Frontend setup
- [ ] Donation form UI
- [ ] Testing
- [ ] Deployment

---

## 💻 Development

### Run Backend Server

```powershell
cd backend
venv\Scripts\activate
python app/main.py
```

### Run Tests

```powershell
pytest
pytest --cov=app
```

### Access API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- FastAPI framework
- React and Material-UI
- PostgreSQL database
- All open-source contributors

---

## 📞 Support

- **Documentation**: Check [docs](docs/) folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/MandirSync/issues)
- **Email**: support@mandirsync.com

---

**Built with ❤️ for Indian Temples**

**Current Status**: 🚧 Active Development - MVP Phase

---

## 🎯 For Developers

### Getting Started Today

1. Follow [Windows Setup Guide](scripts/setup_windows.md)
2. Setup database
3. Run backend server
4. Start building donation module!

### Time Estimate

- **MVP**: 6-8 weeks (with 4-5 hrs/day)
- **Full System**: 4-6 months

---

**Ready to build? Let's go!** 🚀
