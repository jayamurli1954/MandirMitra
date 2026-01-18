-- Migration script to create audit_logs table
-- Run this script to enable comprehensive audit trail

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    user_name VARCHAR(200) NOT NULL,
    user_email VARCHAR(100) NOT NULL,
    user_role VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    changes JSONB,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_id ON audit_logs(entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_role ON audit_logs(user_role);

-- Add comments
COMMENT ON TABLE audit_logs IS 'Comprehensive audit trail of all user actions';
COMMENT ON COLUMN audit_logs.user_id IS 'ID of user who performed the action';
COMMENT ON COLUMN audit_logs.user_name IS 'Name of user (denormalized for performance)';
COMMENT ON COLUMN audit_logs.user_email IS 'Email of user (denormalized for performance)';
COMMENT ON COLUMN audit_logs.user_role IS 'Role of user (denormalized for performance)';
COMMENT ON COLUMN audit_logs.action IS 'Action type: CREATE_DONATION, UPDATE_SEVA, etc.';
COMMENT ON COLUMN audit_logs.entity_type IS 'Type of entity: Donation, SevaBooking, etc.';
COMMENT ON COLUMN audit_logs.entity_id IS 'ID of the affected entity';
COMMENT ON COLUMN audit_logs.old_values IS 'Previous state (JSON)';
COMMENT ON COLUMN audit_logs.new_values IS 'New state (JSON)';
COMMENT ON COLUMN audit_logs.changes IS 'Diff of what changed (JSON)';
COMMENT ON COLUMN audit_logs.ip_address IS 'IP address of user';
COMMENT ON COLUMN audit_logs.user_agent IS 'Browser/client information';
COMMENT ON COLUMN audit_logs.description IS 'Human-readable description of action';










