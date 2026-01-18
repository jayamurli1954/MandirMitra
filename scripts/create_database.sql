-- MandirSync - Database Creation Script
-- Run this in PostgreSQL

-- Create database
CREATE DATABASE temple_db;

-- Connect to database
\c temple_db;

-- Create extensions (if needed)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create user (optional - or use postgres user)
-- CREATE USER temple_user WITH PASSWORD 'temple_password';
-- GRANT ALL PRIVILEGES ON DATABASE temple_db TO temple_user;

-- Note: Tables will be created automatically by SQLAlchemy
-- when you run the FastAPI application

-- Verify connection
SELECT version();


