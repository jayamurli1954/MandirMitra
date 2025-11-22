"""
Seed script to populate Sevas from Sri Varadanjaneva Swamy Temple
Based on temple seva list
"""

from app.core.database import SessionLocal, engine, Base
from app.models.seva import Seva, SevaCategory, SevaAvailability

# Create all tables
Base.metadata.create_all(bind=engine)

def seed_sevas():
    db = SessionLocal()

    # Check if sevas already exist
    existing_count = db.query(Seva).count()
    if existing_count > 0:
        print(f"Sevas already exist ({existing_count} sevas found). Skipping seed.")
        db.close()
        return

    sevas_data = [
        {
            "name_english": "Rathotsava Seva",
            "name_kannada": "ರಥೋತ್ಸವ ಸೇವೆ",
            "description": "Chariot festival seva - Grand procession of the deity",
            "category": SevaCategory.SPECIAL,
            "amount": 15000.00,
            "availability": SevaAvailability.SPECIFIC_DAY,
            "specific_day": 2,  # Tuesday
            "benefits": "Fulfill wishes, remove obstacles, bring prosperity",
            "instructions": "Available only on Tuesdays",
            "duration_minutes": 120
        },
        {
            "name_english": "Shashwatha Pooja Moolanidhi",
            "name_kannada": "ಶಾಶ್ವತ ಪೂಜಾ ಮೂಲನಿಧಿ",
            "description": "Perpetual pooja endowment",
            "category": SevaCategory.SPECIAL,
            "amount": 3000.00,
            "benefits": "Eternal blessings, continuous divine grace",
            "duration_minutes": 60
        },
        {
            "name_english": "Pallaki Seva",
            "name_kannada": "ಪಲ್ಲಕ್ಕಿ ಸೇವೆ",
            "description": "Palanquin procession seva",
            "category": SevaCategory.SPECIAL,
            "amount": 5000.00,
            "availability": SevaAvailability.SPECIFIC_DAY,
            "specific_day": 6,  # Saturday
            "benefits": "Divine blessings, family prosperity",
            "instructions": "Available only on Saturdays",
            "duration_minutes": 90
        },
        {
            "name_english": "Sarva Seva",
            "name_kannada": "ಸರ್ವ ಸೇವೆ",
            "description": "Complete comprehensive seva including all rituals",
            "category": SevaCategory.SPECIAL,
            "amount": 2000.00,
            "benefits": "Overall well-being, spiritual upliftment",
            "duration_minutes": 90
        },
        {
            "name_english": "Navaneetha Alankara",
            "name_kannada": "ನವನೀತ ಅಲಂಕಾರ",
            "description": "Butter decoration of the deity",
            "category": SevaCategory.ALANKARA,
            "amount": 2500.00,
            "availability": SevaAvailability.EXCEPT_DAY,
            "except_day": 6,  # Except Saturday
            "benefits": "Health, happiness, Krishna's grace",
            "instructions": "Not available on Saturdays",
            "duration_minutes": 45
        },
        {
            "name_english": "Sindhura Alankara",
            "name_kannada": "ಸಿಂಧೂರ ಅಲಂಕಾರ",
            "description": "Vermilion decoration",
            "category": SevaCategory.ALANKARA,
            "amount": 1900.00,
            "benefits": "Marital bliss, family harmony",
            "duration_minutes": 30
        },
        {
            "name_english": "Talla / Machu Abhisheka",
            "name_kannada": "ತಲೆ / ಮಚ್ಚು ಅಭಿಷೇಕ",
            "description": "Oil bath abhisheka",
            "category": SevaCategory.ABHISHEKA,
            "amount": 750.00,
            "benefits": "Health, longevity, prosperity",
            "duration_minutes": 45
        },
        {
            "name_english": "Vishasha Pooja",
            "name_kannada": "ವಿಶೇಷ ಪೂಜೆ",
            "description": "Special detailed pooja",
            "category": SevaCategory.POOJA,
            "amount": 800.00,
            "benefits": "Fulfill specific wishes, divine blessings",
            "duration_minutes": 60
        },
        {
            "name_english": "Vada Mala",
            "name_kannada": "ವಡೆ ಮಾಲೆ",
            "description": "Garland of vadas offering",
            "category": SevaCategory.SPECIAL,
            "amount": 400.00,
            "time_slot": "Evening",
            "benefits": "Sweet success, happiness",
            "instructions": "Available only in the evening",
            "duration_minutes": 20
        },
        {
            "name_english": "Panchamrutha Abhisheka",
            "name_kannada": "ಪಂಚಾಮೃತ ಅಭಿಷೇಕ",
            "description": "Five sacred nectars abhisheka (milk, curd, ghee, honey, sugar)",
            "category": SevaCategory.ABHISHEKA,
            "amount": 250.00,
            "benefits": "Purification, divine grace, prosperity",
            "duration_minutes": 30
        },
        {
            "name_english": "Vahana Pooja",
            "name_kannada": "ವಾಹನ ಪೂಜೆ",
            "description": "Pooja to the deity's vehicle",
            "category": SevaCategory.VAHANA_SEVA,
            "amount": 300.00,
            "min_amount": 200.00,
            "max_amount": 400.00,
            "benefits": "Safe travel, vehicle protection",
            "duration_minutes": 30
        },
        {
            "name_english": "Sathyanarayana Pooja",
            "name_kannada": "ಸತ್ಯನಾರಾಯಣ ಪೂಜೆ",
            "description": "Sacred Satyanarayana Vratam pooja",
            "category": SevaCategory.POOJA,
            "amount": 100.00,
            "benefits": "Truth prevails, prosperity, happiness",
            "duration_minutes": 90
        },
        {
            "name_english": "Sankashtahara Pooja",
            "name_kannada": "ಸಂಕಷ್ಟಹರ ಪೂಜೆ",
            "description": "Ganesha pooja to remove obstacles",
            "category": SevaCategory.POOJA,
            "amount": 100.00,
            "benefits": "Remove obstacles, success in endeavors",
            "duration_minutes": 45
        },
        {
            "name_english": "Prasada Seva",
            "name_kannada": "ಪ್ರಸಾದ ಸೇವೆ",
            "description": "Sacred food offering and distribution",
            "category": SevaCategory.SPECIAL,
            "amount": 400.00,
            "benefits": "Divine grace through sacred food",
            "duration_minutes": 30
        },
        {
            "name_english": "Sri Nagadevara Pooja",
            "name_kannada": "ಶ್ರೀ ನಾಗದೇವರ ಪೂಜೆ",
            "description": "Serpent deity worship",
            "category": SevaCategory.POOJA,
            "amount": 200.00,
            "benefits": "Protection from doshas, family well-being",
            "duration_minutes": 45
        },
        {
            "name_english": "Navagraha Pooja",
            "name_kannada": "ನವಗ್ರಹ ಪೂಜೆ",
            "description": "Nine planets worship",
            "category": SevaCategory.POOJA,
            "amount": 300.00,
            "benefits": "Planetary peace, remove doshas, overall well-being",
            "duration_minutes": 60
        },
        {
            "name_english": "Kunkumarchana",
            "name_kannada": "ಕುಂಕುಮಾರ್ಚನೆ",
            "description": "Kumkum offering archana",
            "category": SevaCategory.ARCHANA,
            "amount": 10.00,
            "benefits": "Goddess blessings, quick divine grace",
            "duration_minutes": 10
        },
        {
            "name_english": "Flower Alankara",
            "name_kannada": "ಪುಷ್ಪ ಅಲಂಕಾರ",
            "description": "Fresh flower decoration",
            "category": SevaCategory.ALANKARA,
            "amount": 100.00,
            "benefits": "Beauty, fragrance, divine aesthetics",
            "duration_minutes": 20
        }
    ]

    # Create sevas
    for seva_data in sevas_data:
        seva = Seva(**seva_data)
        db.add(seva)

    db.commit()
    print(f"Successfully seeded {len(sevas_data)} sevas!")
    db.close()

if __name__ == "__main__":
    print("Seeding sevas...")
    seed_sevas()
    print("Done!")
