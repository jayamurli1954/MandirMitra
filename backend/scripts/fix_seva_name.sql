-- Fix incorrect seva name: Talla / Machu Abhisheka -> Taila / Madhu Abhisheka
-- Kannada: ತಲೆ / ಮಚ್ಚು ಅಭಿಷೇಕ -> ತೈಲ / ಮಧು ಅಭಿಷೇಕ

UPDATE sevas 
SET 
    name_english = 'Taila / Madhu Abhisheka',
    name_kannada = 'ತೈಲ / ಮಧು ಅಭಿಷೇಕ',
    updated_at = NOW()
WHERE 
    name_english = 'Talla / Machu Abhisheka' 
    OR name_kannada = 'ತಲೆ / ಮಚ್ಚು ಅಭಿಷೇಕ';

-- Verify the update
SELECT id, name_english, name_kannada, amount 
FROM sevas 
WHERE name_english LIKE '%Taila%' OR name_english LIKE '%Talla%';


























