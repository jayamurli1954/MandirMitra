-- Migration script to add reschedule fields to seva_bookings table
-- Run this script to add the new fields for postpone/prepone functionality

-- Add reschedule fields
ALTER TABLE seva_bookings 
ADD COLUMN IF NOT EXISTS original_booking_date DATE,
ADD COLUMN IF NOT EXISTS reschedule_requested_date DATE,
ADD COLUMN IF NOT EXISTS reschedule_reason TEXT,
ADD COLUMN IF NOT EXISTS reschedule_approved BOOLEAN,
ADD COLUMN IF NOT EXISTS reschedule_approved_by INTEGER REFERENCES users(id),
ADD COLUMN IF NOT EXISTS reschedule_approved_at TIMESTAMP;

-- Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_seva_bookings_reschedule_approved 
ON seva_bookings(reschedule_approved) 
WHERE reschedule_approved IS NULL;

-- Add comment
COMMENT ON COLUMN seva_bookings.original_booking_date IS 'Original booking date before reschedule';
COMMENT ON COLUMN seva_bookings.reschedule_requested_date IS 'Requested new date for reschedule';
COMMENT ON COLUMN seva_bookings.reschedule_reason IS 'Reason provided for reschedule request';
COMMENT ON COLUMN seva_bookings.reschedule_approved IS 'NULL = not requested, TRUE = approved, FALSE = rejected';
COMMENT ON COLUMN seva_bookings.reschedule_approved_by IS 'Admin user ID who approved/rejected';
COMMENT ON COLUMN seva_bookings.reschedule_approved_at IS 'Timestamp when approval/rejection was done';







