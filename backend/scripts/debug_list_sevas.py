
import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app.core.database import SessionLocal
# Import all models to ensure mappers are initialized
from app.models.user import User
from app.models.accounting import Account
from app.models.seva import Seva

def list_sevas():
    db = SessionLocal()
    try:
        sevas = db.query(Seva).all()
        print(f"Total Sevas: {len(sevas)}")
        for seva in sevas:
            print(f"- {seva.name_english} ({seva.category})")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_sevas()
