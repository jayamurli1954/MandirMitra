"""
Script to find and remove duplicate devotee entries
Specifically for phone number 7865123456 - remove Rajan Rao, keep Harini Rao
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.devotee import Devotee
from app.models.donation import Donation
from app.models.seva import SevaBooking

def cleanup_duplicate_devotee():
    """Find and remove duplicate devotee entries for phone 7865123456"""
    db = SessionLocal()
    
    try:
        # Find all devotees with phone 7865123456
        phone_number = '7865123456'
        devotees = db.query(Devotee).filter(Devotee.phone == phone_number).all()
        
        print(f"\nFound {len(devotees)} devotee(s) with phone {phone_number}:")
        for d in devotees:
            print(f"  ID: {d.id}, Name: {d.name}, First: {d.first_name}, Last: {d.last_name}, Created: {d.created_at}")
        
        if len(devotees) <= 1:
            print("\nNo duplicates found. Only one devotee exists with this phone number.")
            return
        
        # Identify which one to keep (Harini Rao) and which to delete (Rajan Rao)
        harini_rao = None
        rajan_rao = None
        
        for d in devotees:
            name_lower = (d.name or '').lower()
            first_name_lower = (d.first_name or '').lower()
            
            if 'harini' in name_lower or 'harini' in first_name_lower:
                harini_rao = d
            elif 'rajan' in name_lower or 'rajan' in first_name_lower:
                rajan_rao = d
        
        if not harini_rao:
            print("\n⚠️  WARNING: Could not find 'Harini Rao'. Please verify manually.")
            print("Available devotees:")
            for d in devotees:
                print(f"  ID: {d.id}, Name: {d.name}")
            return
        
        if not rajan_rao:
            print("\n⚠️  WARNING: Could not find 'Rajan Rao'. Please verify manually.")
            return
        
        print(f"\n✓ Found Harini Rao: ID {harini_rao.id}, Name: {harini_rao.name}")
        print(f"✓ Found Rajan Rao: ID {rajan_rao.id}, Name: {rajan_rao.name}")
        
        # Check if Rajan Rao has any donations or bookings
        donations_count = db.query(Donation).filter(Donation.devotee_id == rajan_rao.id).count()
        bookings_count = db.query(SevaBooking).filter(SevaBooking.devotee_id == rajan_rao.id).count()
        
        print(f"\nRajan Rao (ID {rajan_rao.id}) has:")
        print(f"  - {donations_count} donation(s)")
        print(f"  - {bookings_count} booking(s)")
        
        if donations_count > 0 or bookings_count > 0:
            print("\n⚠️  WARNING: Rajan Rao has transactions. Transferring to Harini Rao...")
            
            # Transfer donations to Harini Rao
            if donations_count > 0:
                db.query(Donation).filter(Donation.devotee_id == rajan_rao.id).update({
                    Donation.devotee_id: harini_rao.id
                })
                print(f"  ✓ Transferred {donations_count} donation(s) to Harini Rao")
            
            # Transfer bookings to Harini Rao
            if bookings_count > 0:
                db.query(SevaBooking).filter(SevaBooking.devotee_id == rajan_rao.id).update({
                    SevaBooking.devotee_id: harini_rao.id
                })
                print(f"  ✓ Transferred {bookings_count} booking(s) to Harini Rao")
        
        # Delete Rajan Rao
        print(f"\n🗑️  Deleting Rajan Rao (ID {rajan_rao.id})...")
        db.delete(rajan_rao)
        db.commit()
        
        print(f"✓ Successfully deleted Rajan Rao (ID {rajan_rao.id})")
        print(f"✓ Harini Rao (ID {harini_rao.id}) is now the only devotee with phone {phone_number}")
        
        # Verify
        remaining = db.query(Devotee).filter(Devotee.phone == phone_number).all()
        print(f"\n✓ Verification: {len(remaining)} devotee(s) remaining with phone {phone_number}")
        for d in remaining:
            print(f"  ID: {d.id}, Name: {d.name}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_duplicate_devotee()







