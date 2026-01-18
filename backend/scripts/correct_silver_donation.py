"""
Script to correct the silver donation (Receipt: TMP001-2025-00045)
- Update donation to properly mark as silver
- Add notes about future use (making silver pallaki)
- Create journal entry correction if needed
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, date
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.core.database import SessionLocal


def correct_silver_donation():
    """Correct the silver donation entry using raw SQL"""
    db: Session = SessionLocal()
    
    try:
        receipt_number = "TMP001-2025-00045"
        
        # Find donation using raw SQL
        result = db.execute(
            text("""
                SELECT id, item_name, item_description, notes, purity, amount, journal_entry_id, temple_id
                FROM donations 
                WHERE receipt_number = :receipt_number
            """),
            {"receipt_number": receipt_number}
        ).first()
        
        if not result:
            print(f"[ERROR] Donation with receipt number {receipt_number} not found!")
            return
        
        donation_id, item_name, item_description, notes, purity, amount, journal_entry_id, temple_id = result
        
        print(f"[OK] Found donation: {receipt_number}")
        print(f"   ID: {donation_id}")
        print(f"   Amount: Rs. {amount:,.2f}")
        print(f"   Current Item Name: {item_name or 'Not set'}")
        print(f"   Current Purity: {purity or 'Not set'}")
        print(f"   Current Notes: {notes[:100] if notes else 'None'}...")
        
        # Check current journal entry
        if journal_entry_id:
            je_result = db.execute(
                text("""
                    SELECT je.id, je.entry_number, je.narration, jl.account_id, jl.debit_amount
                    FROM journal_entries je
                    JOIN journal_lines jl ON jl.journal_entry_id = je.id
                    WHERE je.id = :je_id AND jl.debit_amount > 0
                """),
                {"je_id": journal_entry_id}
            ).first()
            
            if je_result:
                je_id, entry_number, narration, account_id, debit_amount = je_result
                print(f"\n[INFO] Current Journal Entry: {entry_number}")
                print(f"   Narration: {narration}")
                
                # Get account details
                acc_result = db.execute(
                    text("SELECT account_code, account_name FROM accounts WHERE id = :acc_id"),
                    {"acc_id": account_id}
                ).first()
                
                if acc_result:
                    acc_code, acc_name = acc_result
                    print(f"   Debit Account: {acc_code} - {acc_name}")
                    if acc_code == '15002':
                        print(f"   [WARNING] Currently debited to Building (15002), should be Temple Gold & Silver (15010)")
        
        # Update donation details
        print("\n[INFO] Updating donation details...")
        
        # Prepare updates
        new_item_name = "Silver" if not item_name or 'silver' not in (item_name or '').lower() else item_name
        if 'silver' not in new_item_name.lower():
            new_item_name = f"{new_item_name} (Silver)"
        
        new_description_parts = []
        if item_description:
            new_description_parts.append(item_description)
        new_description_parts.append("Silver donation - to be used for making silver pallaki (to cover the wooden pallaki)")
        new_item_description = " | ".join(new_description_parts)
        
        new_notes_parts = []
        if notes:
            new_notes_parts.append(notes)
        new_notes_parts.append(f"Corrected on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Silver donation - to be issued later to make silver pallaki (to cover the wooden pallaki)")
        new_notes = "\n".join(new_notes_parts)
        
        new_purity = purity if purity else "925"
        
        # Update donation
        db.execute(
            text("""
                UPDATE donations 
                SET item_name = :item_name,
                    item_description = :item_description,
                    notes = :notes,
                    purity = :purity,
                    updated_at = :updated_at
                WHERE id = :donation_id
            """),
            {
                "donation_id": donation_id,
                "item_name": new_item_name,
                "item_description": new_item_description,
                "notes": new_notes,
                "purity": new_purity,
                "updated_at": datetime.utcnow().isoformat()
            }
        )
        
        print(f"   [OK] Updated item_name to: {new_item_name}")
        print(f"   [OK] Updated item_description")
        print(f"   [OK] Added notes about future use")
        print(f"   [OK] Set purity to: {new_purity}")
        
        # Check if journal entry correction is needed
        # If journal_entry_id is None, try to find journal entry by reference_id
        if not journal_entry_id and temple_id:
            je_by_ref = db.execute(
                text("SELECT id FROM journal_entries WHERE reference_id = :donation_id"),
                {"donation_id": donation_id}
            ).first()
            if je_by_ref:
                journal_entry_id = je_by_ref[0]
                print(f"[DEBUG] Found journal entry by reference: {journal_entry_id}")
        
        print(f"\n[DEBUG] Checking journal entry: journal_entry_id={journal_entry_id}, temple_id={temple_id}")
        if journal_entry_id and temple_id:
            # Get debit account details directly with account code
            je_result = db.execute(
                text("""
                    SELECT jl.account_id, jl.debit_amount, a.account_code, a.account_name
                    FROM journal_lines jl
                    JOIN accounts a ON a.id = jl.account_id
                    WHERE jl.journal_entry_id = :je_id AND jl.debit_amount > 0
                """),
                {"je_id": journal_entry_id}
            ).first()
            
            if je_result:
                wrong_account_id, debit_amount, account_code, account_name = je_result
                print(f"[DEBUG] Found journal line - Account: {account_code} ({account_name}), Amount: {debit_amount}")
                
                if account_code == '15002':
                    print("\n[INFO] Creating journal entry correction...")
                    
                    # Get correct account (15010)
                    correct_acc_result = db.execute(
                        text("SELECT id FROM accounts WHERE temple_id = :temple_id AND account_code = '15010'"),
                        {"temple_id": temple_id}
                    ).first()
                    
                    if not correct_acc_result:
                        print(f"   [WARNING] Account 15010 (Temple Gold & Silver) not found!")
                        print(f"   Please create this account in Chart of Accounts first.")
                    else:
                        correct_account_id = correct_acc_result[0]
                        
                        # Get credit account from original entry
                        credit_result = db.execute(
                            text("""
                                SELECT jl.account_id 
                                FROM journal_lines jl
                                WHERE jl.journal_entry_id = :je_id AND jl.credit_amount > 0
                            """),
                            {"je_id": journal_entry_id}
                        ).first()
                        
                        if credit_result:
                            # Generate correction entry number
                            year = date.today().year
                            prefix = f"JE/{year}/"
                            last_entry = db.execute(
                                text("""
                                    SELECT entry_number FROM journal_entries 
                                    WHERE temple_id = :temple_id AND entry_number LIKE :prefix
                                    ORDER BY id DESC LIMIT 1
                                """),
                                {"temple_id": temple_id, "prefix": f"{prefix}%"}
                            ).first()
                            
                            if last_entry:
                                try:
                                    last_num = int(last_entry[0].split('/')[-1])
                                    new_num = last_num + 1
                                except:
                                    new_num = 1
                            else:
                                new_num = 1
                            
                            entry_number = f"{prefix}{new_num:04d}"
                            
                            # Get created_by from donation
                            created_by_result = db.execute(
                                text("SELECT created_by FROM donations WHERE id = :donation_id"),
                                {"donation_id": donation_id}
                            ).first()
                            created_by = created_by_result[0] if created_by_result and created_by_result[0] else 1
                            
                            # Create correction journal entry
                            db.execute(
                                text("""
                                    INSERT INTO journal_entries 
                                    (temple_id, entry_date, entry_number, narration, reference_type, reference_id, total_amount, status, created_by, posted_by, posted_at)
                                    VALUES 
                                    (:temple_id, :entry_date, :entry_number, :narration, CAST(:ref_type AS transactiontype), :ref_id, :amount, CAST(:status AS journalentrystatus), :created_by, :posted_by, :posted_at)
                                """),
                                {
                                    "temple_id": temple_id,
                                    "entry_date": datetime.now(),
                                    "entry_number": entry_number,
                                    "narration": f"Correction: Transfer silver donation from Building to Temple Gold & Silver (Receipt: {receipt_number})",
                                    "ref_type": "MANUAL",
                                    "ref_id": donation_id,
                                    "amount": amount,
                                    "status": "POSTED",
                                    "created_by": created_by,
                                    "posted_by": created_by,
                                    "posted_at": datetime.utcnow()
                                }
                            )
                            
                            # Get the new journal entry ID
                            new_je_result = db.execute(
                                text("SELECT id FROM journal_entries WHERE entry_number = :entry_number"),
                                {"entry_number": entry_number}
                            ).first()
                            new_je_id = new_je_result[0]
                            
                            # Create journal lines
                            # Dr: Temple Gold & Silver (15010)
                            db.execute(
                                text("""
                                    INSERT INTO journal_lines 
                                    (journal_entry_id, account_id, debit_amount, credit_amount)
                                    VALUES 
                                    (:je_id, :acc_id, :debit, 0)
                                """),
                                {
                                    "je_id": new_je_id,
                                    "acc_id": correct_account_id,
                                    "debit": amount
                                }
                            )
                            
                            # Cr: Building (15002) - reversing the wrong entry
                            db.execute(
                                text("""
                                    INSERT INTO journal_lines 
                                    (journal_entry_id, account_id, debit_amount, credit_amount)
                                    VALUES 
                                    (:je_id, :acc_id, 0, :credit)
                                """),
                                {
                                    "je_id": new_je_id,
                                    "acc_id": wrong_account_id,
                                    "credit": amount
                                }
                            )
                            
                            # Get account names for display
                            correct_acc_name = db.execute(
                                text("SELECT account_name FROM accounts WHERE id = :acc_id"),
                                {"acc_id": correct_account_id}
                            ).first()[0]
                            
                            wrong_acc_name = db.execute(
                                text("SELECT account_name FROM accounts WHERE id = :acc_id"),
                                {"acc_id": wrong_account_id}
                            ).first()[0]
                            
                            print(f"   [OK] Created correction journal entry: {entry_number}")
                            print(f"      Dr: 15010 - {correct_acc_name} (Rs. {amount:,.2f})")
                            print(f"      Cr: 15002 - {wrong_acc_name} (Rs. {amount:,.2f})")
        
        # Commit all changes
        db.commit()
        
        print("\n[SUCCESS] Donation correction completed successfully!")
        print(f"\n[SUMMARY]")
        print(f"   Receipt: {receipt_number}")
        print(f"   Item Name: {new_item_name}")
        print(f"   Purity: {new_purity}")
        print(f"   Notes: {new_notes[:100]}..." if len(new_notes) > 100 else f"   Notes: {new_notes}")
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Silver Donation Correction Script")
    print("=" * 60)
    print(f"Receipt Number: TMP001-2025-00045")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    correct_silver_donation()
