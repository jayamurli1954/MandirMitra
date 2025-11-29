-- Migration: Add Inventory Management Tables
-- Date: 2025-11-26
-- Description: Creates tables for inventory management (stores, items, stock balances, stock movements)

-- Stores/Locations Table
CREATE TABLE IF NOT EXISTS stores (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id),
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    inventory_account_id INTEGER REFERENCES accounts(id),
    created_at VARCHAR,
    updated_at VARCHAR
);

CREATE INDEX IF NOT EXISTS idx_stores_temple_id ON stores(temple_id);
CREATE INDEX IF NOT EXISTS idx_stores_code ON stores(code);

-- Items Master Table
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id),
    code VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    reorder_level FLOAT DEFAULT 0.0,
    reorder_quantity FLOAT DEFAULT 0.0,
    standard_cost FLOAT DEFAULT 0.0,
    hsn_code VARCHAR(20),
    gst_rate FLOAT DEFAULT 0.0,
    inventory_account_id INTEGER REFERENCES accounts(id),
    expense_account_id INTEGER REFERENCES accounts(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at VARCHAR,
    updated_at VARCHAR
);

CREATE INDEX IF NOT EXISTS idx_items_temple_id ON items(temple_id);
CREATE INDEX IF NOT EXISTS idx_items_code ON items(code);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);

-- Stock Balances Table
CREATE TABLE IF NOT EXISTS stock_balances (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id),
    item_id INTEGER NOT NULL REFERENCES items(id),
    store_id INTEGER NOT NULL REFERENCES stores(id),
    quantity FLOAT NOT NULL DEFAULT 0.0,
    value FLOAT NOT NULL DEFAULT 0.0,
    last_movement_date DATE,
    last_movement_id INTEGER REFERENCES stock_movements(id),
    created_at VARCHAR,
    updated_at VARCHAR,
    UNIQUE(item_id, store_id)
);

CREATE INDEX IF NOT EXISTS idx_stock_balances_temple_id ON stock_balances(temple_id);
CREATE INDEX IF NOT EXISTS idx_stock_balances_item_id ON stock_balances(item_id);
CREATE INDEX IF NOT EXISTS idx_stock_balances_store_id ON stock_balances(store_id);

-- Stock Movements Table
CREATE TABLE IF NOT EXISTS stock_movements (
    id SERIAL PRIMARY KEY,
    temple_id INTEGER REFERENCES temples(id),
    movement_type VARCHAR(50) NOT NULL,
    movement_number VARCHAR(50) UNIQUE NOT NULL,
    movement_date DATE NOT NULL,
    item_id INTEGER NOT NULL REFERENCES items(id),
    store_id INTEGER NOT NULL REFERENCES stores(id),
    to_store_id INTEGER REFERENCES stores(id),
    quantity FLOAT NOT NULL,
    unit_price FLOAT DEFAULT 0.0,
    total_value FLOAT NOT NULL,
    reference_number VARCHAR(100),
    vendor_id INTEGER REFERENCES vendors(id),
    issued_to VARCHAR(200),
    purpose VARCHAR(200),
    notes TEXT,
    journal_entry_id INTEGER REFERENCES journal_entries(id),
    created_by INTEGER REFERENCES users(id),
    created_at VARCHAR,
    updated_at VARCHAR
);

CREATE INDEX IF NOT EXISTS idx_stock_movements_temple_id ON stock_movements(temple_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_type ON stock_movements(movement_type);
CREATE INDEX IF NOT EXISTS idx_stock_movements_number ON stock_movements(movement_number);
CREATE INDEX IF NOT EXISTS idx_stock_movements_date ON stock_movements(movement_date);
CREATE INDEX IF NOT EXISTS idx_stock_movements_item_id ON stock_movements(item_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_store_id ON stock_movements(store_id);




