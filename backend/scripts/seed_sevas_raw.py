
import sys
import os
import datetime
from sqlalchemy import create_engine, text

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app.core.config import settings

def seed_sevas_raw():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    # Check if sevas exist
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT count(*) FROM sevas"))
            count = result.scalar()
            if count > 0:
                print(f"Sevas already exist ({count} found). Skipping seed.")
                return
        except Exception as e:
            print(f"Error checking count: {e}")
            return

    # Data
    sevas_data = [
        {
            "name_english": "Rathotsava Seva",
            "name_kannada": "ರಥೋತ್ಸವ ಸೇವೆ",
            "description": "Chariot festival seva - Grand procession of the deity",
            "category": "special",
            "amount": 15000.00,
            "availability": "specific_day",
            "specific_day": 2,  # Tuesday
            "benefits": "Fulfill wishes, remove obstacles, bring prosperity",
            "instructions": "Available only on Tuesdays",
            "duration_minutes": 120
        },
        {
            "name_english": "Shashwatha Pooja Moolanidhi",
            "name_kannada": "ಶಾಶ್ವತ ಪೂಜಾ ಮೂಲನಿಧಿ",
            "description": "Perpetual pooja endowment",
            "category": "special",
            "amount": 3000.00,
            "benefits": "Eternal blessings, continuous divine grace",
            "duration_minutes": 60
        },
        {
            "name_english": "Pallaki Seva",
            "name_kannada": "ಪಲ್ಲಕ್ಕಿ ಸೇವೆ",
            "description": "Palanquin procession seva",
            "category": "special",
            "amount": 5000.00,
            "availability": "specific_day",
            "specific_day": 6,  # Saturday
            "benefits": "Divine blessings, family prosperity",
            "instructions": "Available only on Saturdays",
            "duration_minutes": 90
        },
        {
            "name_english": "Sarva Seva",
            "name_kannada": "ಸರ್ವ ಸೇವೆ",
            "description": "Complete comprehensive seva including all rituals",
            "category": "special",
            "amount": 2000.00,
            "benefits": "Overall well-being, spiritual upliftment",
            "duration_minutes": 90
        },
        {
            "name_english": "Navaneetha Alankara",
            "name_kannada": "ನವನೀತ ಅಲಂಕಾರ",
            "description": "Butter decoration of the deity",
            "category": "alankara",
            "amount": 2500.00,
            "availability": "except_day",
            "except_day": 6,  # Except Saturday
            "benefits": "Health, happiness, Krishna's grace",
            "instructions": "Not available on Saturdays",
            "duration_minutes": 45
        },
        {
            "name_english": "Sindhura Alankara",
            "name_kannada": "ಸಿಂಧೂರ ಅಲಂಕಾರ",
            "description": "Vermilion decoration",
            "category": "alankara",
            "amount": 1900.00,
            "benefits": "Marital bliss, family harmony",
            "duration_minutes": 30
        },
        {
            "name_english": "Taila / Madhu Abhisheka",
            "name_kannada": "ತೈಲ / ಮಧು ಅಭಿಷೇಕ",
            "description": "Oil bath abhisheka",
            "category": "abhisheka",
            "amount": 750.00,
            "benefits": "Health, longevity, prosperity",
            "duration_minutes": 45
        },
        {
            "name_english": "Vishasha Pooja",
            "name_kannada": "ವಿಶೇಷ ಪೂಜೆ",
            "description": "Special detailed pooja",
            "category": "pooja",
            "amount": 800.00,
            "benefits": "Fulfill specific wishes, divine blessings",
            "duration_minutes": 60
        },
        {
            "name_english": "Vada Mala",
            "name_kannada": "ವಡೆ ಮಾಲೆ",
            "description": "Garland of vadas offering",
            "category": "special",
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
            "category": "abhisheka",
            "amount": 250.00,
            "benefits": "Purification, divine grace, prosperity",
            "duration_minutes": 30
        },
        {
            "name_english": "Vahana Pooja",
            "name_kannada": "ವಾಹನ ಪೂಜೆ",
            "description": "Pooja to the deity's vehicle",
            "category": "vahana_seva",
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
            "category": "pooja",
            "amount": 100.00,
            "benefits": "Truth prevails, prosperity, happiness",
            "duration_minutes": 90
        },
        {
            "name_english": "Sankashtahara Pooja",
            "name_kannada": "ಸಂಕಷ್ಟಹರ ಪೂಜೆ",
            "description": "Ganesha pooja to remove obstacles",
            "category": "pooja",
            "amount": 100.00,
            "benefits": "Remove obstacles, success in endeavors",
            "duration_minutes": 45
        },
        {
            "name_english": "Prasada Seva",
            "name_kannada": "ಪ್ರಸಾದ ಸೇವೆ",
            "description": "Sacred food offering and distribution",
            "category": "special",
            "amount": 400.00,
            "benefits": "Divine grace through sacred food",
            "duration_minutes": 30
        },
        {
            "name_english": "Sri Nagadevara Pooja",
            "name_kannada": "ಶ್ರೀ ನಾಗದೇವರ ಪೂಜೆ",
            "description": "Serpent deity worship",
            "category": "pooja",
            "amount": 200.00,
            "benefits": "Protection from doshas, family well-being",
            "duration_minutes": 45
        },
        {
            "name_english": "Navagraha Pooja",
            "name_kannada": "ನವಗ್ರಹ ಪೂಜೆ",
            "description": "Nine planets worship",
            "category": "pooja",
            "amount": 300.00,
            "benefits": "Planetary peace, remove doshas, overall well-being",
            "duration_minutes": 60
        },
        {
            "name_english": "Kunkumarchana",
            "name_kannada": "ಕುಂಕುಮಾರ್ಚನೆ",
            "description": "Kumkum offering archana",
            "category": "archana",
            "amount": 10.00,
            "benefits": "Goddess blessings, quick divine grace",
            "duration_minutes": 10
        },
        {
            "name_english": "Flower Alankara",
            "name_kannada": "ಪುಷ್ಪ ಅಲಂಕಾರ",
            "description": "Fresh flower decoration",
            "category": "alankara",
            "amount": 100.00,
            "benefits": "Beauty, fragrance, divine aesthetics",
            "duration_minutes": 20
        }
    ]

    sql = text("""
        INSERT INTO sevas (
            name_english, name_kannada, description, category, amount, 
            min_amount, max_amount, availability, specific_day, except_day, 
            time_slot, benefits, instructions, duration_minutes, 
            advance_booking_days, requires_approval, is_active, is_token_seva,
            created_at, updated_at
        ) VALUES (
            :name_english, :name_kannada, :description, :category, :amount, 
            :min_amount, :max_amount, :availability, :specific_day, :except_day, 
            :time_slot, :benefits, :instructions, :duration_minutes, 
            30, false, true, false,
            now(), now()
        )
    """)

    use_uppercase = False
    
    print("Determining Enum Case strategy...")
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            test_item = sevas_data[0]
            conn.execute(sql, {
                "name_english": "TEST_SEVA_TEMP",
                "name_kannada": None,
                "description": None,
                "category": test_item["category"].lower(), 
                "amount": 100,
                "min_amount": None,
                "max_amount": None,
                "availability": "daily", 
                "specific_day": None,
                "except_day": None,
                "time_slot": None,
                "benefits": None,
                "instructions": None,
                "duration_minutes": None
            })
            print("Lowercase category detected.")
            trans.rollback()
            use_uppercase = False
        except Exception as e:
            msg = str(e).lower()
            print(f"Lowercase insertion failed: {e}")
            trans.rollback()
            if "enum" in msg or "input value" in msg:
                 print("Will try UPPERCASE.")
                 use_uppercase = True
    
    print(f"Starting Seed with UPPERCASE={use_uppercase}...")
    with engine.connect() as conn:
        trans = conn.begin()
        count_inserted = 0
        try:
            for data in sevas_data:
                category_val = data["category"]
                availability_val = data.get("availability", "daily")
                
                if use_uppercase:
                    category_val = category_val.upper()
                    availability_val = availability_val.upper()

                params = {
                    "name_english": data["name_english"],
                    "name_kannada": data.get("name_kannada"),
                    "description": data.get("description"),
                    "category": category_val,
                    "amount": data["amount"],
                    "min_amount": data.get("min_amount"),
                    "max_amount": data.get("max_amount"),
                    "availability": availability_val,
                    "specific_day": data.get("specific_day"),
                    "except_day": data.get("except_day"),
                    "time_slot": data.get("time_slot"),
                    "benefits": data.get("benefits"),
                    "instructions": data.get("instructions"),
                    "duration_minutes": data.get("duration_minutes")
                }
                
                conn.execute(sql, params)
                count_inserted += 1
                print(f"Inserted: {data['name_english']}")
            
            trans.commit()
            print(f"Successfully inserted {count_inserted} sevas!")
        except Exception as e:
            print(f"Seed failed: {e}")
            trans.rollback()

if __name__ == "__main__":
    seed_sevas_raw()
