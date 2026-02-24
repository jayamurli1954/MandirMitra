# MandirMitra Backend

FastAPI backend for Temple Management System.

## Setup (Windows)

### 1. Create Virtual Environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment

```powershell
# Copy example environment file
copy .env.example .env

# Edit .env with your settings
notepad .env
```

### 4. Setup Database

```powershell
# Create database in PostgreSQL
psql -U postgres
CREATE DATABASE temple_db;
\q

# Update DATABASE_URL in .env:
# DATABASE_URL=postgresql://postgres:your_password@localhost:5432/temple_db
```

### 5. Run Server

```powershell
# Development mode (with hot reload)
python -m uvicorn app.main:app --reload

# Or simply
python app/main.py
```

### 6. Access API

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database connection
│   │   └── security.py      # Auth utilities
│   ├── models/              # SQLAlchemy models
│   │   ├── temple.py
│   │   ├── user.py
│   │   ├── devotee.py
│   │   └── donation.py
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes
│   ├── services/            # Business logic
│   └── utils/               # Utilities
├── tests/                   # Tests
├── .env                     # Environment variables
├── .env.example             # Environment template
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Development

### Run Tests

```powershell
pytest
pytest --cov=app
```

### Database Migrations (with Alembic - to be setup)

```powershell
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## API Endpoints (To be built)

### Authentication
- POST `/api/v1/auth/register` - Register user
- POST `/api/v1/auth/login` - Login
- POST `/api/v1/auth/logout` - Logout

### Donations
- POST `/api/v1/donations` - Create donation
- GET `/api/v1/donations` - List donations
- GET `/api/v1/donations/{id}` - Get donation
- GET `/api/v1/donations/report/daily` - Daily report

### Devotees
- POST `/api/v1/devotees` - Create devotee
- GET `/api/v1/devotees` - List devotees
- GET `/api/v1/devotees/{id}` - Get devotee
- PUT `/api/v1/devotees/{id}` - Update devotee

## Troubleshooting

### Database Connection Error

```
Error: could not connect to server
```

Solution: Ensure PostgreSQL is running and credentials in .env are correct.

### Module Not Found

```
ModuleNotFoundError: No module named 'app'
```

Solution: Make sure you're in the backend directory and virtual environment is activated.

### Port Already in Use

```
Error: [Errno 10048] Only one usage of each socket address...
```

Solution: Change PORT in .env or stop the application using port 8000.


