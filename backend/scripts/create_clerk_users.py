"""
Script to create clerk users for standalone version
Creates clerk1, clerk2, clerk3, etc. with default passwords
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.models.user import User
from app.models.temple import Temple
from app.core.security import get_password_hash
from datetime import datetime


def create_clerk_users(num_clerks: int = 3, default_password: str = "clerk123"):
    """
    Create clerk users for standalone version
    
    Args:
        num_clerks: Number of clerk users to create (default: 3)
        default_password: Default password for all clerks (default: "clerk123")
    """
    db: Session = SessionLocal()
    
    try:
        # Get or create temple (for standalone)
        temple = db.query(Temple).first()
        if not temple:
            print("No temple found. Please create a temple first.")
            return
        
        print(f"Creating {num_clerks} clerk users for temple: {temple.name}")
        print("=" * 60)
        
        created_count = 0
        skipped_count = 0
        
        for i in range(1, num_clerks + 1):
            email = f"clerk{i}@temple.local"
            full_name = f"Clerk {i}"
            
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                print(f"⚠️  User {email} already exists. Skipping...")
                skipped_count += 1
                continue
            
            # Create clerk user
            clerk = User(
                email=email,
                password_hash=get_password_hash(default_password),
                full_name=full_name,
                role="staff",  # or "clerk" if you have that role
                is_active=True,
                temple_id=temple.id,
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            )
            
            db.add(clerk)
            db.commit()
            db.refresh(clerk)
            
            print(f"✅ Created: {full_name}")
            print(f"   Email: {email}")
            print(f"   Password: {default_password}")
            print(f"   Role: {clerk.role}")
            print()
            
            created_count += 1
        
        print("=" * 60)
        print(f"Summary:")
        print(f"  Created: {created_count}")
        print(f"  Skipped: {skipped_count}")
        print()
        print(f"⚠️  IMPORTANT: Change default passwords after first login!")
        print()
        
    except Exception as e:
        print(f"❌ Error creating clerk users: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create clerk users for standalone version")
    parser.add_argument(
        "--num-clerks",
        type=int,
        default=3,
        help="Number of clerk users to create (default: 3)"
    )
    parser.add_argument(
        "--password",
        type=str,
        default="clerk123",
        help="Default password for all clerks (default: clerk123)"
    )
    
    args = parser.parse_args()
    
    create_clerk_users(num_clerks=args.num_clerks, default_password=args.password)

