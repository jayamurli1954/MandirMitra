-- Script to find and remove duplicate devotee "Rajan Rao" for phone 7865123456
-- Keep "Harini Rao", remove "Rajan Rao"

-- First, check what we have
SELECT id, name, first_name, last_name, phone, created_at 
FROM devotees 
WHERE phone = '7865123456'
ORDER BY id;

-- Transfer any donations from Rajan Rao to Harini Rao
-- (Replace IDs with actual IDs from above query)
-- UPDATE donations SET devotee_id = <harini_rao_id> WHERE devotee_id = <rajan_rao_id>;

-- Transfer any bookings from Rajan Rao to Harini Rao
-- UPDATE bookings SET devotee_id = <harini_rao_id> WHERE devotee_id = <rajan_rao_id>;

-- Delete Rajan Rao (replace <rajan_rao_id> with actual ID)
-- DELETE FROM devotees WHERE id = <rajan_rao_id> AND (name ILIKE '%rajan%' OR first_name ILIKE '%rajan%');

-- Verify cleanup
-- SELECT id, name, first_name, last_name, phone FROM devotees WHERE phone = '7865123456';







