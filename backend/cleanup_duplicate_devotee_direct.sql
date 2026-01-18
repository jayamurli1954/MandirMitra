-- Direct SQL script to find and remove duplicate devotee "Rajan Rao" for phone 7865123456
-- Keep "Harini Rao", remove "Rajan Rao"

-- Step 1: Check what we have
SELECT id, name, first_name, last_name, phone, created_at, 
       (SELECT COUNT(*) FROM donations WHERE devotee_id = devotees.id) as donation_count,
       (SELECT COUNT(*) FROM bookings WHERE devotee_id = devotees.id) as booking_count
FROM devotees 
WHERE phone = '7865123456'
ORDER BY id;

-- Step 2: Identify IDs (replace with actual IDs from Step 1)
-- Example: If Harini Rao has ID=5 and Rajan Rao has ID=10:

-- Step 3: Transfer donations from Rajan Rao to Harini Rao (replace IDs)
-- UPDATE donations SET devotee_id = <harini_rao_id> WHERE devotee_id = <rajan_rao_id>;

-- Step 4: Transfer bookings from Rajan Rao to Harini Rao (replace IDs)
-- UPDATE bookings SET devotee_id = <harini_rao_id> WHERE devotee_id = <rajan_rao_id>;

-- Step 5: Delete Rajan Rao (replace <rajan_rao_id> with actual ID)
-- DELETE FROM devotees WHERE id = <rajan_rao_id> AND (name ILIKE '%rajan%' OR first_name ILIKE '%rajan%');

-- Step 6: Verify cleanup
-- SELECT id, name, first_name, last_name, phone FROM devotees WHERE phone = '7865123456';







