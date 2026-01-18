# MandirMitra - Temple Management System - Technical Architecture

**Version:** 1.0  
**Last Updated:** November 17, 2025  
**Status:** Active Development

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [Database Design](#database-design)
6. [API Design](#api-design)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)
9. [Scalability Strategy](#scalability-strategy)
10. [Monitoring & Observability](#monitoring--observability)

---

## System Overview

### Architecture Style
**Monolithic with Microservices Preparation**

- Phase 1-2: Monolithic FastAPI application
- Phase 3+: Gradual extraction to microservices

**Rationale:**
- Start simple for faster MVP
- Monolith easier to develop and debug
- Can extract services later as needed
- Avoid premature optimization

### Multi-Tenancy Approach
**Shared Database, Isolated Data**

- Single application instance serves multiple temples
- Each temple has unique `temple_id`
- Data isolation at row level (temple_id in every table)
- Shared codebase, temple-specific configuration

**Benefits:**
- Lower infrastructure costs
- Easier maintenance
- Consistent features across temples
- Centralized updates

---

## Architecture Principles

### 1. **Simplicity First**
- Start with simplest solution that works
- Add complexity only when needed
- Favor convention over configuration

### 2. **Security by Design**
- Authentication on every endpoint
- Encryption at rest and in transit
- Input validation everywhere
- Principle of least privilege

### 3. **Fail Gracefully**
- Comprehensive error handling
- User-friendly error messages
- Automatic retries for transient failures
- Circuit breakers for external services

### 4. **Observability**
- Structured logging
- Metrics collection
- Distributed tracing
- Real-time monitoring

### 5. **Scalability**
- Stateless application servers
- Database read replicas
- Caching layer
- Horizontal scaling ready

### 6. **Testability**
- Unit tests for business logic
- Integration tests for APIs
- End-to-end tests for critical flows
- 80% code coverage target

---

## System Architecture

### High-Level Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
├────────────────┬───────────────────┬──────────────────────────┤
│  Web Admin     │  Public Website   │  Mobile App (Flutter)     │
│  (React + MUI) │  (React)          │  (Future Phase)           │
│                │                   │                           │
│  - Dashboard   │  - Seva Booking   │  - Devotee Portal        │
│  - Donations   │  - Online Donate  │  - Seva Booking          │
│  - Reports     │  - Event Calendar │  - Live Darshan          │
│  - Config      │  - Contact        │  - Notifications         │
└────────────────┴───────────────────┴──────────────────────────┘
                           │
                           ↓ HTTPS (TLS 1.3)
┌────────────────────────────────────────────────────────────────┐
│                    Load Balancer (NGINX)                        │
│  - SSL Termination                                              │
│  - Rate Limiting                                                │
│  - DDoS Protection                                              │
└────────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────────────┐
│                  Application Layer (FastAPI)                    │
├────────────────┬───────────────────┬──────────────────────────┤
│  Auth Module   │  Core Module      │  Integration Module      │
│  - Login       │  - Donations      │  - Payment Gateway       │
│  - Register    │  - Sevas          │  - SMS/Email             │
│  - JWT         │  - Bookings       │  - WhatsApp              │
│  - Permissions │  - Devotees       │  - Tally Export          │
│                │  - Reports        │                          │
│                │                   │                          │
│  Accounting    │  Inventory        │  Notification Module     │
│  - Vouchers    │  - Stock          │  - Queue (Celery)        │
│  - Ledger      │  - GRN/GIN        │  - SMS Worker            │
│  - Reports     │  - Valuation      │  - Email Worker          │
└────────────────┴───────────────────┴──────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────────────┐
│                    Caching Layer (Redis)                        │
│  - Session Storage                                              │
│  - API Response Cache                                           │
│  - Rate Limiting Counters                                       │
│  - Real-time Data                                               │
└────────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────────────┐
│                  Database Layer (PostgreSQL)                    │
├────────────────┬───────────────────┬──────────────────────────┤
│  Primary DB    │  Read Replica 1   │  Read Replica 2          │
│  (Master)      │  (Reports)        │  (Analytics)             │
│  - Writes      │  - Heavy Queries  │  - Dashboard             │
│  - Reads       │  - Exports        │  - BI Tools              │
└────────────────┴───────────────────┴──────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────────────┐
│                    Object Storage (AWS S3 / MinIO)              │
│  - Receipts (PDF)                                               │
│  - Images (Temple, Deity, Seva)                                │
│  - Backups                                                      │
│  - Documents                                                    │
└────────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────────────┐
│                   Message Queue (RabbitMQ)                      │
│  - Async Tasks (Email, SMS, Reports)                           │
│  - Background Jobs                                              │
│  - Event-driven Processing                                      │
└────────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────────────┐
│                 External Services                               │
├────────────────┬───────────────────┬──────────────────────────┤
│  Razorpay      │  Twilio (SMS)     │  SendGrid (Email)        │
│  (Payments)    │  MSG91            │  AWS SES                 │
│                │                   │                          │
│  WhatsApp API  │  Google Maps      │  AWS CloudWatch          │
│  (Meta)        │  (Optional)       │  (Monitoring)            │
└────────────────┴───────────────────┴──────────────────────────┘
```

---

## Technology Stack

### Backend Stack

#### Core Framework
```yaml
Language: Python 3.11+
Framework: FastAPI 0.104+
ASGI Server: Uvicorn
Process Manager: Gunicorn (production)
```

**Why FastAPI?**
- Modern, high-performance
- Automatic API documentation (Swagger)
- Type hints and validation (Pydantic)
- Async support (better concurrency)
- Easy to learn (especially with Python background)

#### Database & ORM
```yaml
Database: PostgreSQL 14+
ORM: SQLAlchemy 2.0+
Migrations: Alembic
Connection Pool: psycopg2-binary
```

**Why PostgreSQL?**
- ACID compliance (critical for financial transactions)
- Superior for complex queries and joins
- Excellent JSON support (for flexible config)
- Battle-tested for accounting systems
- Better for reporting and analytics

#### Caching & Queue
```yaml
Cache: Redis 7+
Message Queue: RabbitMQ / Redis Queue
Task Worker: Celery
Scheduler: Celery Beat
```

#### Authentication & Security
```yaml
Auth: JWT (PyJWT)
Password Hashing: Passlib (bcrypt)
Environment: python-dotenv
Secrets: HashiCorp Vault (optional)
```

#### API & Validation
```yaml
Validation: Pydantic v2
API Client: httpx (async)
Payment SDK: razorpay-python
SMS: twilio, msg91-python
Email: sendgrid, AWS SES boto3
```

#### Testing
```yaml
Unit Tests: pytest
API Tests: pytest + httpx
Coverage: pytest-cov
Mocking: pytest-mock
Fixtures: pytest-fixtures
```

#### Code Quality
```yaml
Linting: ruff
Formatting: black
Type Checking: mypy
Security: bandit
Pre-commit: pre-commit hooks
```

---

### Frontend Stack

#### Core Framework
```yaml
Framework: React 18+
Build Tool: Vite
Language: TypeScript (optional) or JavaScript
Package Manager: npm or yarn
```

#### UI Library
```yaml
Component Library: Material-UI (MUI) v5
Icons: MUI Icons / Lucide React
Styling: Emotion (MUI's default)
Layout: MUI Grid / Stack
```

#### State Management
```yaml
Global State: Zustand or Redux Toolkit
Server State: TanStack Query (React Query)
Form State: React Hook Form
```

**Why Zustand?**
- Simpler than Redux
- Less boilerplate
- Better TypeScript support
- Smaller bundle size

#### Routing & Navigation
```yaml
Router: React Router v6
Protected Routes: Custom HOC
Navigation Guards: useAuth hook
```

#### HTTP & API
```yaml
HTTP Client: Axios
API Config: Axios interceptors
Request Retry: axios-retry
```

#### Forms & Validation
```yaml
Forms: React Hook Form
Validation: Zod or Yup
Date Picker: MUI Date Pickers
Rich Text: TipTap or Slate
```

#### Data Visualization
```yaml
Charts: Recharts or Chart.js
Tables: MUI Data Grid
Export: xlsx, jsPDF
```

#### Testing
```yaml
Unit: Vitest or Jest
Component: React Testing Library
E2E: Cypress or Playwright
```

---

### Mobile Stack (Future Phase)

```yaml
Framework: Flutter 3.0+
Language: Dart
State: Riverpod or Bloc
HTTP: Dio
Local DB: Hive or SQLite
Storage: Secure Storage
Notifications: Firebase Cloud Messaging
```

---

### DevOps & Infrastructure

#### Containerization
```yaml
Container: Docker
Orchestration: Docker Compose (dev)
Registry: Docker Hub / AWS ECR
```

#### CI/CD
```yaml
Pipeline: GitHub Actions
Testing: Automated on PR
Deployment: Auto-deploy on merge
Environments: dev, staging, production
```

#### Hosting (Recommended: DigitalOcean)
```yaml
App Server: Droplets (2GB RAM minimum)
Database: Managed PostgreSQL
Cache: Managed Redis
Load Balancer: DO Load Balancer
CDN: Cloudflare
Storage: Spaces (S3-compatible)
```

**Cost Estimate:**
- Starter: $25/month (1 temple)
- Growth: $100/month (10 temples)
- Scale: $500/month (100+ temples)

#### Monitoring & Logging
```yaml
Error Tracking: Sentry
Logging: ELK Stack or Loki
Metrics: Prometheus + Grafana
Uptime: UptimeRobot
APM: New Relic (optional)
```

#### Backups
```yaml
Database: Daily automated backups
Retention: 30 days
Storage: S3 or DO Spaces
Restore: Documented procedure
```

---

## Database Design

### Database Architecture

```
┌──────────────────────────────────────┐
│         PostgreSQL Cluster            │
├──────────────────────────────────────┤
│                                       │
│  ┌────────────────────────────────┐ │
│  │   Primary (Master)             │ │
│  │   - All Writes                 │ │
│  │   - Real-time Reads            │ │
│  └────────────┬───────────────────┘ │
│               │                      │
│               │ Replication          │
│               ↓                      │
│  ┌────────────────────────────────┐ │
│  │   Read Replica 1               │ │
│  │   - Reports                    │ │
│  │   - Analytics                  │ │
│  └────────────────────────────────┘ │
│                                       │
│  ┌────────────────────────────────┐ │
│  │   Read Replica 2 (Optional)    │ │
│  │   - Exports                    │ │
│  │   - Heavy Queries              │ │
│  └────────────────────────────────┘ │
└──────────────────────────────────────┘
```

### Database Schema Overview

See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for detailed schema.

#### Core Tables (15+)

1. **temples** - Temple master data
2. **users** - System users (admin, staff, priests)
3. **roles** - User roles
4. **permissions** - Role permissions
5. **devotees** - Devotee information
6. **donation_categories** - Donation types
7. **donations** - Donation transactions
8. **sevas** - Seva catalog
9. **bookings** - Seva bookings
10. **receipts** - Receipt generation tracking
11. **transactions** - Payment transactions
12. **accounting_ledgers** - Account ledgers
13. **accounting_vouchers** - Financial vouchers
14. **inventory_items** - Stock items
15. **assets** - Temple assets
16. **hundi_collections** - Hundi opening records
17. **notifications** - Notification log
18. **audit_logs** - System audit trail

### Indexing Strategy

```sql
-- Critical indexes for performance

-- Fast devotee lookup
CREATE INDEX idx_devotees_phone ON devotees(phone);
CREATE INDEX idx_devotees_email ON devotees(email);

-- Donation queries
CREATE INDEX idx_donations_temple_date ON donations(temple_id, donation_date);
CREATE INDEX idx_donations_devotee ON donations(devotee_id);
CREATE INDEX idx_donations_receipt ON donations(receipt_number);

-- Booking queries
CREATE INDEX idx_bookings_temple_date ON bookings(temple_id, booking_date);
CREATE INDEX idx_bookings_devotee ON bookings(devotee_id);
CREATE INDEX idx_bookings_seva ON bookings(seva_id);

-- Multi-tenant isolation
CREATE INDEX idx_donations_temple ON donations(temple_id);
CREATE INDEX idx_bookings_temple ON bookings(temple_id);
CREATE INDEX idx_sevas_temple ON sevas(temple_id);

-- Full-text search (for devotee names)
CREATE INDEX idx_devotees_name_fts ON devotees USING gin(to_tsvector('english', name));
```

### Partitioning Strategy (Future)

For large temples with millions of transactions:

```sql
-- Partition donations by year
CREATE TABLE donations_2025 PARTITION OF donations
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE donations_2026 PARTITION OF donations
FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
```

---

## API Design

### API Architecture

#### RESTful Principles

- Resource-based URLs
- HTTP methods: GET, POST, PUT, DELETE
- Status codes: 2xx success, 4xx client error, 5xx server error
- JSON request/response

#### Versioning

```
/api/v1/donations
/api/v2/donations (future)
```

#### Authentication

All endpoints require JWT token except:
- `/api/v1/auth/login`
- `/api/v1/auth/register`
- `/api/v1/public/*` (public website)

**Token Header:**
```
Authorization: Bearer <jwt_token>
```

#### Request/Response Format

**Success Response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "amount": 1000
  },
  "message": "Donation recorded successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid phone number",
    "details": {
      "field": "phone",
      "issue": "Must be 10 digits"
    }
  }
}
```

#### Pagination

```
GET /api/v1/donations?page=1&limit=50
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 1000,
    "pages": 20
  }
}
```

#### Filtering & Sorting

```
GET /api/v1/donations?date_from=2025-01-01&date_to=2025-01-31&sort=-donation_date
```

#### Rate Limiting

- 1000 requests/hour per user
- 10,000 requests/hour per temple
- Response headers:
  ```
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 950
  X-RateLimit-Reset: 1640000000
  ```

---

## Security Architecture

### Authentication Flow

```
┌─────────┐                                   ┌─────────┐
│ Client  │                                   │  Server │
└────┬────┘                                   └────┬────┘
     │                                             │
     │  1. POST /auth/login                       │
     │  { email, password }                       │
     ├────────────────────────────────────────────>
     │                                             │
     │  2. Verify credentials                     │
     │  3. Generate JWT (2h expiry)               │
     │  4. Generate Refresh Token (7d expiry)     │
     │                                             │
     │  <─────────────────────────────────────────┤
     │  { access_token, refresh_token }           │
     │                                             │
     │  5. Store tokens (localStorage/memory)     │
     │                                             │
     │  6. API Request                            │
     │  Header: Authorization: Bearer <token>     │
     ├────────────────────────────────────────────>
     │                                             │
     │  7. Verify JWT signature                   │
     │  8. Check expiry                           │
     │  9. Extract user info                      │
     │                                             │
     │  <─────────────────────────────────────────┤
     │  { data }                                  │
     │                                             │
     │  10. Token expired?                        │
     │  POST /auth/refresh                        │
     │  { refresh_token }                         │
     ├────────────────────────────────────────────>
     │                                             │
     │  <─────────────────────────────────────────┤
     │  { new_access_token }                      │
     │                                             │
```

### Authorization (RBAC)

```python
# Permission decorator
@router.post("/donations")
@require_permission("donation.create")
async def create_donation(...):
    pass

# Role hierarchy
SUPER_ADMIN > TEMPLE_MANAGER > ACCOUNTANT > COUNTER_STAFF
```

### Data Encryption

1. **At Rest:**
   - Database: PostgreSQL encryption
   - Sensitive fields: AES-256
   - Backups: Encrypted

2. **In Transit:**
   - HTTPS/TLS 1.3
   - API: SSL certificate
   - Database: SSL connection

### Input Validation

```python
from pydantic import BaseModel, validator, Field

class DonationCreate(BaseModel):
    devotee_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., regex=r'^\d{10}$')
    amount: float = Field(..., gt=0, lt=10000000)
    
    @validator('phone')
    def validate_phone(cls, v):
        if not v.isdigit():
            raise ValueError('Phone must be digits only')
        return v
```

### SQL Injection Prevention

- Use SQLAlchemy ORM (parameterized queries)
- Never concatenate SQL strings
- Input validation

### XSS Prevention

- React auto-escapes by default
- Sanitize HTML input
- Content Security Policy headers

### CSRF Protection

- CSRF tokens for state-changing operations
- SameSite cookies
- Double-submit cookies

---

## Deployment Architecture

### Development Environment

```yaml
Setup: Docker Compose
Services:
  - FastAPI (hot reload)
  - PostgreSQL
  - Redis
  - RabbitMQ
  - MailHog (email testing)
```

```bash
# Start all services
docker-compose up

# Access
Backend: http://localhost:8000
Frontend: http://localhost:3000
API Docs: http://localhost:8000/docs
Database: localhost:5432
```

### Production Environment (DigitalOcean Example)

```
┌─────────────────────────────────────────┐
│         Cloudflare (CDN + DDoS)         │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│      Load Balancer (DO LB + NGINX)      │
│      - SSL Termination                   │
│      - Health Checks                     │
└────────────────┬────────────────────────┘
                 │
         ┌───────┴────────┐
         ↓                ↓
┌────────────────┐  ┌────────────────┐
│ App Server 1   │  │ App Server 2   │
│ (Droplet)      │  │ (Droplet)      │
│ - Docker       │  │ - Docker       │
│ - FastAPI      │  │ - FastAPI      │
│ - Celery       │  │ - Celery       │
└────────────────┘  └────────────────┘
         │                │
         └───────┬────────┘
                 ↓
┌─────────────────────────────────────────┐
│   Managed PostgreSQL (DO)               │
│   - Primary + Replica                    │
│   - Automated Backups                    │
└─────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│   Managed Redis (DO)                     │
└─────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│   Spaces (S3-compatible Storage)         │
│   - Images, PDFs, Backups                │
└─────────────────────────────────────────┘
```

### Docker Configuration

**Dockerfile (FastAPI):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ./app ./app

# Run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/temple_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --reload --host 0.0.0.0

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=temple_db
      - POSTGRES_USER=temple_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm start

volumes:
  postgres_data:
```

---

## Scalability Strategy

### Horizontal Scaling

1. **Stateless Application Servers**
   - No session state in application
   - Sessions in Redis
   - Can add/remove servers dynamically

2. **Load Balancing**
   - Round-robin distribution
   - Health checks
   - Auto-scaling based on CPU/memory

3. **Database Scaling**
   - Read replicas for reports
   - Connection pooling
   - Query optimization

### Caching Strategy

```python
# Cache expensive queries
@cache(expire=300)  # 5 minutes
def get_seva_catalog(temple_id):
    return db.query(Seva).filter_by(temple_id=temple_id).all()

# Cache donation stats
@cache(expire=60)  # 1 minute
def get_daily_stats(temple_id, date):
    return calculate_stats(temple_id, date)

# Invalidate on update
@app.post("/sevas")
def create_seva(...):
    seva = create_new_seva(...)
    cache.delete(f"seva_catalog:{temple_id}")
    return seva
```

### Async Processing

```python
# Background tasks with Celery

@celery_app.task
def send_donation_receipt(donation_id):
    donation = get_donation(donation_id)
    pdf = generate_receipt_pdf(donation)
    send_email(donation.devotee.email, pdf)
    send_sms(donation.devotee.phone, receipt_link)

# Call from API
@app.post("/donations")
def create_donation(...):
    donation = save_donation(...)
    send_donation_receipt.delay(donation.id)  # Async
    return donation
```

---

## Monitoring & Observability

### Application Monitoring

```python
# Sentry for error tracking
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### Logging

```python
import structlog

logger = structlog.get_logger()

# Structured logging
logger.info(
    "donation_created",
    donation_id=donation.id,
    temple_id=temple.id,
    amount=donation.amount,
    payment_mode=donation.payment_mode
)
```

### Metrics

```python
from prometheus_client import Counter, Histogram

donation_counter = Counter('donations_total', 'Total donations')
donation_amount = Histogram('donation_amount', 'Donation amounts')

@app.post("/donations")
def create_donation(...):
    donation = save_donation(...)
    
    # Track metrics
    donation_counter.inc()
    donation_amount.observe(donation.amount)
    
    return donation
```

### Health Checks

```python
@app.get("/health")
def health_check():
    # Check database
    try:
        db.execute("SELECT 1")
    except:
        return {"status": "unhealthy", "database": "down"}
    
    # Check Redis
    try:
        redis.ping()
    except:
        return {"status": "unhealthy", "redis": "down"}
    
    return {"status": "healthy"}
```

---

## Development Best Practices

### Code Organization

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── database.py          # DB connection
│   │
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── temple.py
│   │   ├── devotee.py
│   │   ├── donation.py
│   │   └── seva.py
│   │
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── donation.py
│   │   └── seva.py
│   │
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── deps.py          # Dependencies
│   │   ├── auth.py
│   │   ├── donations.py
│   │   └── sevas.py
│   │
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── donation_service.py
│   │   └── payment_service.py
│   │
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── auth.py
│       └── receipt.py
│
├── alembic/                 # Migrations
├── tests/
└── requirements.txt
```

### Testing Strategy

```python
# Unit tests
def test_create_donation():
    donation = DonationService.create(
        devotee_id=1,
        amount=1000,
        category="General"
    )
    assert donation.id is not None
    assert donation.amount == 1000

# API tests
def test_donation_api(client):
    response = client.post("/api/v1/donations", json={
        "devotee_name": "Test",
        "phone": "9876543210",
        "amount": 1000,
        "category": "General",
        "payment_mode": "Cash"
    })
    assert response.status_code == 200
    assert response.json()["success"] == True
```

### Git Workflow

```bash
# Feature branch
git checkout -b feature/seva-booking

# Commit with conventional commits
git commit -m "feat: add seva booking endpoint"
git commit -m "fix: validate booking date"
git commit -m "docs: update API documentation"

# Pull request
# CI runs tests automatically
# Code review
# Merge to main
```

---

## Disaster Recovery

### Backup Strategy

1. **Database Backups:**
   - Automated daily backups
   - Retention: 30 days
   - Storage: S3 or DO Spaces
   - Encryption: AES-256

2. **Application Backups:**
   - Docker images tagged by version
   - Config files in secure storage

3. **Recovery Procedures:**
   - RTO (Recovery Time Objective): 4 hours
   - RPO (Recovery Point Objective): 15 minutes
   - Documented restoration process

### Failover Strategy

1. **Database:**
   - Automatic failover to replica
   - Manual promotion if needed

2. **Application:**
   - Multiple app servers
   - Load balancer health checks
   - Auto-restart failed containers

---

## Performance Optimization

### Database Optimization

- Proper indexing
- Query optimization
- Connection pooling
- Prepared statements
- Batch operations

### Application Optimization

- Async/await for I/O
- Caching frequently accessed data
- Lazy loading
- Pagination
- Response compression

### Frontend Optimization

- Code splitting
- Lazy loading routes
- Image optimization
- CDN for static assets
- Service worker (PWA)

---

## Future Architecture Evolution

### Phase 1: Monolith (Months 1-6)
- Single FastAPI application
- Shared database
- Simple deployment

### Phase 2: Modular Monolith (Months 7-12)
- Clear module boundaries
- Separate services (still same app)
- Preparation for microservices

### Phase 3: Microservices (Year 2+)
- Extract high-load services
- API gateway
- Service mesh
- Event-driven architecture

**Potential Microservices:**
- Auth Service
- Payment Service
- Notification Service
- Reporting Service

---

**Document Maintained By:** Technical Team  
**Last Review:** November 17, 2025  
**Next Review:** December 17, 2025

---
