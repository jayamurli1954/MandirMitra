# Database Schema - MandirMitra - Temple Management System

**Version:** 1.0  
**Database:** PostgreSQL 14+  
**Last Updated:** November 17, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [ER Diagram](#er-diagram)
3. [Core Tables](#core-tables)
4. [Relationships](#relationships)
5. [Indexes](#indexes)
6. [Constraints](#constraints)
7. [Sample Data](#sample-data)

---

## Overview

### Multi-Tenant Architecture

Every table (except `temples`) includes a `temple_id` column to enable multi-tenancy:
- Single database serves multiple temples
- Row-level data isolation
- Temple-specific queries always filter by `temple_id`

### Naming Conventions

- **Tables:** Plural, lowercase, snake_case (e.g., `donations`, `seva_bookings`)
- **Primary Keys:** `id` (integer, auto-increment)
- **Foreign Keys:** `{table}_id` (e.g., `devotee_id`, `seva_id`)
- **Timestamps:** `created_at`, `updated_at` (both timestamptz)
- **Soft Deletes:** `deleted_at` (timestamptz, nullable)

---

## ER Diagram

```
┌──────────────┐
│   temples    │
└──────┬───────┘
       │
       ├─────────────────┐
       │                 │
       ↓                 ↓
┌─────────────┐   ┌──────────────┐
│    users    │   │  devotees    │
└──────┬──────┘   └──────┬───────┘
       │                 │
       │                 ├──────────────┐
       │                 │              │
       ↓                 ↓              ↓
┌──────────────┐   ┌─────────────┐  ┌─────────────┐
│    roles     │   │  donations  │  │  bookings   │
└──────────────┘   └─────────────┘  └──────┬──────┘
                                            │
                   ┌──────────────┐         │
                   │    sevas     │◄────────┘
                   └──────────────┘
```

---

## Core Tables

### 1. temples

Master temple data. Each temple is a separate tenant.

```sql
CREATE TABLE temples (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    primary_deity VARCHAR(100),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    phone VARCHAR(20),
    email VARCHAR(100),
    website VARCHAR(200),
    registration_number VARCHAR(100),
    trust_name VARCHAR(200),
    chairman_name VARCHAR(100),
    chairman_phone VARCHAR(20),
    chairman_email VARCHAR(100),
    opening_time TIME,
    closing_time TIME,
    logo_url VARCHAR(500),
    banner_url VARCHAR(500),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_temples_slug ON temples(slug);
CREATE INDEX idx_temples_active ON temples(is_active);
```

**Sample Data:**
```sql
INSERT INTO temples (name, slug, primary_deity, city, state) VALUES
('Tirupati Balaji Temple', 'tirupati-balaji', 'Lord Venkateswara', 'Tirupati', 'Andhra Pradesh'),
('Siddhivinayak Temple', 'siddhivinayak', 'Lord Ganesha', 'Mumbai', 'Maharashtra');
```

---

### 2. users

System users (admins, staff, priests).

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER NOT NULL REFERENCES temples(id) ON DELETE CASCADE,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'staff',
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    last_password_change TIMESTAMPTZ DEFAULT NOW(),
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_temple ON users(temple_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- User roles: super_admin, temple_manager, accountant, counter_staff, priest
```

---

### 3. devotees

Devotee information and CRM.

```sql
CREATE TABLE devotees (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100),
    full_name VARCHAR(200) NOT NULL,
    gothra VARCHAR(100),
    nakshatra VARCHAR(100),
    date_of_birth DATE,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    country VARCHAR(100) DEFAULT 'India',
    profile_image_url VARCHAR(500),
    notes TEXT,
    tags TEXT[], -- Array of tags for segmentation
    is_vip BOOLEAN DEFAULT FALSE,
    total_donations DECIMAL(12,2) DEFAULT 0,
    total_bookings INTEGER DEFAULT 0,
    last_visit_date DATE,
    communication_preference VARCHAR(20) DEFAULT 'sms', -- sms, email, whatsapp, none
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_devotees_temple ON devotees(temple_id);
CREATE INDEX idx_devotees_phone ON devotees(phone);
CREATE INDEX idx_devotees_email ON devotees(email);
CREATE INDEX idx_devotees_name ON devotees USING gin(to_tsvector('english', full_name));
CREATE INDEX idx_devotees_tags ON devotees USING gin(tags);
```

---

### 4. donation_categories

Configurable donation categories per temple.

```sql
CREATE TABLE donation_categories (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER NOT NULL REFERENCES temples(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_80g_eligible BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(temple_id, name)
);

CREATE INDEX idx_donation_categories_temple ON donation_categories(temple_id);
```

**Sample Data:**
```sql
INSERT INTO donation_categories (temple_id, name, is_80g_eligible) VALUES
(1, 'General Donation', TRUE),
(1, 'Annadanam', TRUE),
(1, 'Construction Fund', TRUE),
(1, 'Gold/Silver Donation', FALSE),
(1, 'Corpus Fund', TRUE);
```

---

### 5. donations

Donation transactions.

```sql
CREATE TABLE donations (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER NOT NULL REFERENCES temples(id) ON DELETE CASCADE,
    devotee_id INTEGER NOT NULL REFERENCES devotees(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES donation_categories(id),
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
    payment_mode VARCHAR(20) NOT NULL, -- cash, card, upi, cheque, online
    transaction_id VARCHAR(100), -- For online payments
    cheque_number VARCHAR(50),
    cheque_date DATE,
    bank_name VARCHAR(100),
    is_anonymous BOOLEAN DEFAULT FALSE,
    notes TEXT,
    donation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    financial_year VARCHAR(10), -- e.g., '2024-25'
    is_cancelled BOOLEAN DEFAULT FALSE,
    cancelled_at TIMESTAMPTZ,
    cancellation_reason TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_donations_temple ON donations(temple_id);
CREATE INDEX idx_donations_devotee ON donations(devotee_id);
CREATE INDEX idx_donations_category ON donations(category_id);
CREATE INDEX idx_donations_date ON donations(donation_date);
CREATE INDEX idx_donations_receipt ON donations(receipt_number);
CREATE INDEX idx_donations_temple_date ON donations(temple_id, donation_date);
CREATE INDEX idx_donations_fy ON donations(financial_year);
```

---

### 6. sevas

Seva/Pooja catalog.

```sql
CREATE TABLE sevas (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER NOT NULL REFERENCES temples(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    name_local VARCHAR(200), -- In regional language
    category VARCHAR(100), -- daily, special, festival
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    duration_minutes INTEGER,
    daily_quota INTEGER DEFAULT 100,
    advance_booking_days INTEGER DEFAULT 30,
    online_booking_enabled BOOLEAN DEFAULT TRUE,
    requires_sankalpam BOOLEAN DEFAULT TRUE,
    image_url VARCHAR(500),
    materials_required TEXT[], -- Array of materials
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sevas_temple ON sevas(temple_id);
CREATE INDEX idx_sevas_active ON sevas(is_active);
CREATE INDEX idx_sevas_category ON sevas(category);
```

**Sample Data:**
```sql
INSERT INTO sevas (temple_id, name, price, duration_minutes, daily_quota) VALUES
(1, 'Suprabhatam Seva', 500, 30, 100),
(1, 'Archana', 100, 10, 500),
(1, 'Abhishekam', 251, 20, 50);
```

---

### 7. bookings

Seva bookings.

```sql
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER NOT NULL REFERENCES temples(id) ON DELETE CASCADE,
    seva_id INTEGER NOT NULL REFERENCES sevas(id) ON DELETE CASCADE,
    devotee_id INTEGER NOT NULL REFERENCES devotees(id) ON DELETE CASCADE,
    booking_number VARCHAR(50) UNIQUE NOT NULL,
    booking_date DATE NOT NULL,
    booking_time TIME,
    devotee_names TEXT[], -- Names of people for whom seva is booked
    gotra VARCHAR(100),
    nakshatra VARCHAR(100),
    sankalpam TEXT,
    amount_paid DECIMAL(10,2) NOT NULL,
    payment_mode VARCHAR(20) NOT NULL,
    transaction_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'confirmed', -- confirmed, cancelled, completed
    is_cancelled BOOLEAN DEFAULT FALSE,
    cancelled_at TIMESTAMPTZ,
    cancellation_reason TEXT,
    refund_amount DECIMAL(10,2),
    refund_transaction_id VARCHAR(100),
    refund_processed_at TIMESTAMPTZ,
    priest_id INTEGER REFERENCES users(id),
    completed_at TIMESTAMPTZ,
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bookings_temple ON bookings(temple_id);
CREATE INDEX idx_bookings_seva ON bookings(seva_id);
CREATE INDEX idx_bookings_devotee ON bookings(devotee_id);
CREATE INDEX idx_bookings_date ON bookings(booking_date);
CREATE INDEX idx_bookings_temple_date ON bookings(temple_id, booking_date);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_priest ON bookings(priest_id);
```

---

### 8. receipts

Receipt generation tracking (for both donations and bookings).

```sql
CREATE TABLE receipts (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER NOT NULL REFERENCES temples(id) ON DELETE CASCADE,
    receipt_type VARCHAR(20) NOT NULL, -- donation, booking
    reference_id INTEGER NOT NULL, -- donation_id or booking_id
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    pdf_url VARCHAR(500),
    is_80g_certificate BOOLEAN DEFAULT FALSE,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    sent_via_sms BOOLEAN DEFAULT FALSE,
    sent_via_email BOOLEAN DEFAULT FALSE,
    sms_sent_at TIMESTAMPTZ,
    email_sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_receipts_temple ON receipts(temple_id);
CREATE INDEX idx_receipts_type_ref ON receipts(receipt_type, reference_id);
CREATE INDEX idx_receipts_number ON receipts(receipt_number);
```

---

### 9. transactions

All payment transactions (for audit trail).

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER NOT NULL REFERENCES temples(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL, -- donation, booking, refund
    reference_id INTEGER NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    payment_mode VARCHAR(20) NOT NULL,
    payment_gateway VARCHAR(50), -- razorpay, paytm, etc.
    gateway_transaction_id VARCHAR(100),
    gateway_order_id VARCHAR(100),
    gateway_payment_id VARCHAR(100),
    gateway_response JSONB, -- Full gateway response
    status VARCHAR(20) DEFAULT 'pending', -- pending, success, failed, refunded
    failure_reason TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transactions_temple ON transactions(temple_id);
CREATE INDEX idx_transactions_type_ref ON transactions(transaction_type, reference_id);
CREATE INDEX idx_transactions_gateway_txn ON transactions(gateway_transaction_id);
CREATE INDEX idx_transactions_status ON transactions(status);
```

---

### 10. audit_logs

System-wide audit trail.

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL, -- login, create_donation, update_seva, etc.
    entity_type VARCHAR(50), -- donation, booking, seva, user
    entity_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_temple ON audit_logs(temple_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
```

---

### 11. temple_config

Temple-specific configuration settings.

```sql
CREATE TABLE temple_config (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER NOT NULL REFERENCES temples(id) ON DELETE CASCADE,
    config_key VARCHAR(100) NOT NULL,
    config_value TEXT,
    data_type VARCHAR(20) DEFAULT 'string', -- string, integer, boolean, json
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(temple_id, config_key)
);

CREATE INDEX idx_temple_config_temple ON temple_config(temple_id);
CREATE INDEX idx_temple_config_key ON temple_config(config_key);
```

**Sample Configuration Keys:**
```sql
INSERT INTO temple_config (temple_id, config_key, config_value, data_type) VALUES
(1, 'receipt_prefix', 'TBT', 'string'),
(1, '80g_enabled', 'true', 'boolean'),
(1, 'fcra_enabled', 'true', 'boolean'),
(1, 'booking_advance_days', '90', 'integer'),
(1, 'theme_color', '#FF6600', 'string'),
(1, 'languages', '["Telugu", "English", "Hindi"]', 'json');
```

---

## Relationships

### Primary Relationships

1. **Temple → Users** (One-to-Many)
   - Each temple has multiple users (admin, staff, priests)

2. **Temple → Devotees** (One-to-Many)
   - Each temple has multiple devotees

3. **Temple → Donations** (One-to-Many)
   - Each temple has multiple donations

4. **Devotee → Donations** (One-to-Many)
   - Each devotee can make multiple donations

5. **Temple → Sevas** (One-to-Many)
   - Each temple has multiple sevas in catalog

6. **Seva → Bookings** (One-to-Many)
   - Each seva can have multiple bookings

7. **Devotee → Bookings** (One-to-Many)
   - Each devotee can make multiple bookings

8. **Donation → Receipt** (One-to-One)
   - Each donation has one receipt

9. **Booking → Receipt** (One-to-One)
   - Each booking has one receipt

---

## Indexes

### Performance-Critical Indexes

Already defined above in table definitions. Key indexes:

1. **Multi-tenant isolation:** `temple_id` on all tables
2. **Date range queries:** `donation_date`, `booking_date`
3. **Lookups:** `phone`, `email`, `receipt_number`
4. **Full-text search:** `devotee.name` using GIN index
5. **Status filtering:** `is_active`, `is_cancelled`, `status`

---

## Constraints

### Check Constraints

```sql
-- Positive amounts
ALTER TABLE donations ADD CONSTRAINT chk_donation_amount_positive 
CHECK (amount > 0);

ALTER TABLE bookings ADD CONSTRAINT chk_booking_amount_positive 
CHECK (amount_paid > 0);

-- Valid payment modes
ALTER TABLE donations ADD CONSTRAINT chk_donation_payment_mode 
CHECK (payment_mode IN ('cash', 'card', 'upi', 'cheque', 'online'));

-- Valid booking status
ALTER TABLE bookings ADD CONSTRAINT chk_booking_status 
CHECK (status IN ('confirmed', 'cancelled', 'completed'));

-- Booking date in future (or today)
ALTER TABLE bookings ADD CONSTRAINT chk_booking_date_future 
CHECK (booking_date >= CURRENT_DATE);
```

### Foreign Key Constraints

All foreign keys are defined with:
- `ON DELETE CASCADE` - When parent deleted, child rows deleted
- `ON DELETE SET NULL` - When parent deleted, FK set to NULL (for audit logs)

---

## Sample Data

See `scripts/seed_data.sql` for complete sample data.

**Quick Sample:**

```sql
-- Sample Temple
INSERT INTO temples (name, slug, primary_deity, city, state) VALUES
('Test Temple', 'test-temple', 'Lord Shiva', 'Bangalore', 'Karnataka')
RETURNING id; -- Note the returned ID

-- Sample User (password: admin123 - hashed with bcrypt)
INSERT INTO users (temple_id, email, password_hash, full_name, role, is_superuser) VALUES
(1, 'admin@testtemple.com', '$2b$12$...', 'Admin User', 'super_admin', TRUE);

-- Sample Devotee
INSERT INTO devotees (temple_id, phone, full_name, email) VALUES
(1, '9876543210', 'Test Devotee', 'devotee@example.com');

-- Sample Donation Category
INSERT INTO donation_categories (temple_id, name) VALUES
(1, 'General Donation');

-- Sample Donation
INSERT INTO donations (temple_id, devotee_id, category_id, receipt_number, amount, payment_mode) VALUES
(1, 1, 1, 'TEST-2025-00001', 1000, 'cash');
```

---

## Views (Optional)

Useful database views for reporting:

```sql
-- Daily collection summary
CREATE VIEW v_daily_collections AS
SELECT 
    temple_id,
    donation_date,
    COUNT(*) as total_donations,
    SUM(amount) as total_amount,
    SUM(CASE WHEN payment_mode = 'cash' THEN amount ELSE 0 END) as cash_amount,
    SUM(CASE WHEN payment_mode != 'cash' THEN amount ELSE 0 END) as digital_amount
FROM donations
WHERE is_cancelled = FALSE
GROUP BY temple_id, donation_date;

-- Devotee statistics
CREATE VIEW v_devotee_stats AS
SELECT 
    d.id,
    d.full_name,
    d.phone,
    COUNT(DISTINCT don.id) as total_donations,
    COALESCE(SUM(don.amount), 0) as lifetime_donation_value,
    COUNT(DISTINCT b.id) as total_bookings,
    MAX(don.donation_date) as last_donation_date,
    MAX(b.booking_date) as last_booking_date
FROM devotees d
LEFT JOIN donations don ON d.id = don.devotee_id AND don.is_cancelled = FALSE
LEFT JOIN bookings b ON d.id = b.devotee_id AND b.is_cancelled = FALSE
GROUP BY d.id, d.full_name, d.phone;
```

---

**Database Schema Maintained By:** Development Team  
**Last Updated:** November 17, 2025

---
