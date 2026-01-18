"""
Sponsorship API Endpoints
Manage devotee sponsorships for temple expenses
Handles both temple payment and direct vendor payment scenarios
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.devotee import Devotee
from app.models.vendor import Vendor
from app.models.inkind_sponsorship import (
    Sponsorship,
    SponsorshipPayment,
    SponsorshipPaymentMode,
    SponsorshipStatus,
)
from app.models.accounting import (
    Account,
    JournalEntry,
    JournalLine,
    JournalEntryStatus,
    TransactionType,
)
from app.schemas.sponsorship import (
    SponsorshipCreate,
    SponsorshipUpdate,
    SponsorshipResponse,
    SponsorshipFulfill,
    SponsorshipPaymentCreate,
    SponsorshipPaymentResponse,
    DirectPaymentRecord,
)

router = APIRouter(prefix="/api/v1/sponsorships", tags=["sponsorships"])


# ===== HELPER FUNCTIONS =====


def generate_sponsorship_receipt_number(db: Session, temple_id: int) -> str:
    """
    Generate unique receipt number for sponsorships
    Format: SP/YYYY/0001
    """
    year = datetime.now().year
    prefix = f"SP/{year}/"

    # Get last receipt number
    last_sponsorship = (
        db.query(Sponsorship)
        .filter(Sponsorship.temple_id == temple_id, Sponsorship.receipt_number.like(f"{prefix}%"))
        .order_by(Sponsorship.id.desc())
        .first()
    )

    if last_sponsorship and last_sponsorship.receipt_number:
        try:
            last_num = int(last_sponsorship.receipt_number.split("/")[-1])
            new_num = last_num + 1
        except:
            new_num = 1
    else:
        new_num = 1

    return f"{prefix}{new_num:04d}"


def post_sponsorship_commitment(
    db: Session, temple_id: int, sponsorship: Sponsorship, current_user: User
) -> Optional[JournalEntry]:
    """
    Post sponsorship commitment to accounting
    Dr. Sponsorship Receivable
       Cr. Sponsorship Income (Committed)
    """
    try:
        # Get sponsorship receivable account
        receivable_account = (
            db.query(Account)
            .filter(
                Account.temple_id == temple_id,
                Account.account_code
                == "21010",  # Sponsorship Receivable (Liability - advance received)
                Account.is_active == True,
            )
            .first()
        )

        # Get sponsorship income account
        income_account = (
            db.query(Account)
            .filter(
                Account.temple_id == temple_id,
                Account.account_code.like("450%"),  # Sponsorship Income
                Account.is_active == True,
            )
            .first()
        )

        if not receivable_account or not income_account:
            print(f"⚠️ Warning: Missing accounts for sponsorship commitment")
            return None

        # Generate entry number
        entry_number = f"JE/{datetime.now().year}/SP{sponsorship.id:04d}"

        # Create journal entry
        narration = f"Sponsorship Commitment - {sponsorship.sponsorship_category}"
        if sponsorship.devotee:
            narration += f" by {sponsorship.devotee.name}"

        journal_entry = JournalEntry(
            entry_number=entry_number,
            entry_date=sponsorship.receipt_date,
            narration=narration,
            reference_type=TransactionType.SPONSORSHIP,
            reference_id=sponsorship.id,
            temple_id=temple_id,
            total_amount=sponsorship.committed_amount,
            status=JournalEntryStatus.POSTED,
            created_by=current_user.id,
            posted_by=current_user.id,
            posted_at=datetime.utcnow(),
        )
        db.add(journal_entry)
        db.flush()

        # Debit: Sponsorship Receivable
        debit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=receivable_account.id,
            debit_amount=sponsorship.committed_amount,
            credit_amount=0.0,
            description=f"Sponsorship commitment - {sponsorship.sponsorship_category}",
        )
        db.add(debit_line)

        # Credit: Sponsorship Income
        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=income_account.id,
            debit_amount=0.0,
            credit_amount=sponsorship.committed_amount,
            description=f"Sponsorship income (committed)",
        )
        db.add(credit_line)

        db.flush()
        return journal_entry

    except Exception as e:
        print(f"❌ Error posting sponsorship commitment: {e}")
        return None


def post_sponsorship_payment(
    db: Session,
    temple_id: int,
    sponsorship: Sponsorship,
    payment: SponsorshipPayment,
    current_user: User,
) -> Optional[JournalEntry]:
    """
    Post sponsorship payment to accounting (for temple_payment mode)

    When devotee pays temple for sponsorship (temple will pay vendor later):
    Dr. Bank/Cash Account
       Cr. Sponsorship Receivable

    Note: When temple later pays vendor, a separate expense entry should be created:
    Dr. Expense Account (e.g., Flower Decoration Expense)
       Cr. Bank/Cash Account
    """
    try:
        # Get cash/bank account based on payment method
        if payment.payment_method.lower() in ["cash", "cash_counter"]:
            asset_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == temple_id,
                    Account.account_code == "11001",  # Cash in Hand - Counter
                    Account.is_active == True,
                )
                .first()
            )
        else:
            # UPI, Bank Transfer, etc.
            asset_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == temple_id,
                    Account.account_code.like("12%"),  # Bank accounts (12000-12999)
                    Account.is_active == True,
                )
                .first()
            )

        # Get sponsorship receivable account
        receivable_account = (
            db.query(Account)
            .filter(
                Account.temple_id == temple_id,
                Account.account_code
                == "21010",  # Sponsorship Receivable (Liability - advance received)
                Account.is_active == True,
            )
            .first()
        )

        if not asset_account or not receivable_account:
            print(f"⚠️ Warning: Missing accounts for sponsorship payment")
            return None

        # Generate entry number
        entry_number = f"JE/{datetime.now().year}/SPP{payment.id:04d}"

        # Create journal entry
        narration = f"Sponsorship Payment - {sponsorship.receipt_number}"
        if sponsorship.devotee:
            narration += f" from {sponsorship.devotee.name}"

        journal_entry = JournalEntry(
            entry_number=entry_number,
            entry_date=payment.payment_date,
            narration=narration,
            reference_type=TransactionType.SPONSORSHIP,
            reference_id=sponsorship.id,
            temple_id=temple_id,
            total_amount=payment.amount_paid,
            status=JournalEntryStatus.POSTED,
            created_by=current_user.id,
            posted_by=current_user.id,
            posted_at=datetime.utcnow(),
        )
        db.add(journal_entry)
        db.flush()

        # Debit: Cash/Bank Account
        debit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=asset_account.id,
            debit_amount=payment.amount_paid,
            credit_amount=0.0,
            description=f"Payment received - {payment.payment_method}",
        )
        db.add(debit_line)

        # Credit: Sponsorship Receivable
        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=receivable_account.id,
            debit_amount=0.0,
            credit_amount=payment.amount_paid,
            description=f"Sponsorship payment received",
        )
        db.add(credit_line)

        db.flush()
        return journal_entry

    except Exception as e:
        print(f"❌ Error posting sponsorship payment: {e}")
        return None


def post_direct_payment_to_vendor(
    db: Session, temple_id: int, sponsorship: Sponsorship, current_user: User
) -> Optional[JournalEntry]:
    """
    Post direct vendor payment to accounting (for direct_payment mode)
    This is a non-cash transaction where devotee paid vendor directly

    Standard Accounting Practice (as per NGO/Trust guidelines):
    Dr. Event Expenses (Flower Decoration/Lighting/Tent, etc.) [FMV]
    Cr. Donation Income - In-Kind Contribution [FMV]

    This ensures:
    - Balance sheet is not affected (no cash movement)
    - Income and Expense accounts correctly reflect the transaction
    - Financial statements show accurate scale of operations
    """
    try:
        # Map sponsorship category to appropriate IN-KIND expense account
        # For in-kind sponsorships, we use special expense accounts (5404-5407) to clearly mark them as non-cash
        category_to_account_code = {
            "flower_decoration": "54006",  # Decoration Expenses
            "lighting": "53002",  # Electricity (lighting)
            "tent": "54005",  # Event Expenses
            "sound_system": "54005",  # Event Expenses
            "decoration": "54006",  # Decoration Expenses
            "event_sponsorship": "54004",  # Festival Expenses
        }

        # Get expense account based on sponsorship category
        category_lower = sponsorship.sponsorship_category.lower().replace(" ", "_")
        expense_account_code = category_to_account_code.get(
            category_lower, "54004"
        )  # Default to Festival Expenses

        # Try in-kind expense account first
        expense_account = (
            db.query(Account)
            .filter(
                Account.temple_id == temple_id,
                Account.account_code == expense_account_code,
                Account.is_active == True,
            )
            .first()
        )

        # If in-kind account doesn't exist, try regular expense account
        if not expense_account and expense_account_code in ["54004", "54005", "54006", "54007"]:
            # Fallback to regular expense accounts
            fallback_codes = {
                "54004": "53002",  # Electricity (for lighting)
                "54005": "54005",  # Event Expenses
                "54006": "54006",  # Decoration Expenses
                "54007": "54007",  # Prasadam Expenses
            }
            fallback_code = fallback_codes.get(expense_account_code, "54004")
            expense_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == temple_id,
                    Account.account_code == fallback_code,
                    Account.is_active == True,
                )
                .first()
            )

        # Fallback: If specific account not found, use first festival/event expense account
        if not expense_account:
            expense_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == temple_id,
                    Account.account_code.like("540%"),  # Festival/Event expenses (54000-54099)
                    Account.is_active == True,
                )
                .first()
            )

        # Final fallback: Any expense account
        if not expense_account:
            expense_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == temple_id,
                    Account.account_code.like("5%"),  # Any expense account (51000-59999)
                    Account.is_active == True,
                )
                .first()
            )

        # Get sponsorship income account - should be "In-Kind Donation Income" (4400) or "In-Kind Sponsorship Income" (4403)
        # Priority: 4403 (In-Kind Sponsorship Income) > 4400 (In-Kind Donation Income) > 4300 (Sponsorship Income)
        income_account = (
            db.query(Account)
            .filter(
                Account.temple_id == temple_id,
                Account.account_code == "45002",  # In-Kind Sponsorship Income (preferred)
                Account.is_active == True,
            )
            .first()
        )

        if not income_account:
            income_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == temple_id,
                    Account.account_code == "44004",  # In-Kind Donation Income
                    Account.is_active == True,
                )
                .first()
            )

        if not income_account:
            income_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == temple_id,
                    Account.account_code == "45001",  # Sponsorship Income
                    Account.is_active == True,
                )
                .first()
            )

        # Final fallback: Any in-kind/sponsorship income account
        if not income_account:
            income_account = (
                db.query(Account)
                .filter(
                    Account.temple_id == temple_id,
                    Account.account_code.in_(["44004", "45002", "45001"]),
                    Account.is_active == True,
                )
                .first()
            )

        if not expense_account or not income_account:
            print(f"⚠️ Warning: Missing accounts for direct vendor payment")
            return None

        # Generate entry number
        entry_number = f"JE/{datetime.now().year}/SPD{sponsorship.id:04d}"

        # Create journal entry
        # Narration follows standard accounting practice for in-kind sponsorships
        narration = f"In-Kind Sponsorship - {sponsorship.sponsorship_category} (FMV: ₹{amount})"
        if sponsorship.devotee:
            narration += f" by {sponsorship.devotee.name}"
        if sponsorship.vendor:
            narration += f" (Vendor: {sponsorship.vendor.vendor_name})"
        if sponsorship.vendor_invoice_number:
            narration += f" [Invoice: {sponsorship.vendor_invoice_number}]"

        journal_entry = JournalEntry(
            entry_number=entry_number,
            entry_date=sponsorship.receipt_date,
            narration=narration,
            reference_type=TransactionType.SPONSORSHIP,
            reference_id=sponsorship.id,
            temple_id=temple_id,
            total_amount=sponsorship.vendor_invoice_amount or sponsorship.committed_amount,
            status=JournalEntryStatus.POSTED,
            created_by=current_user.id,
            posted_by=current_user.id,
            posted_at=datetime.utcnow(),
        )
        db.add(journal_entry)
        db.flush()

        amount = sponsorship.vendor_invoice_amount or sponsorship.committed_amount

        # Debit: Expense Account
        debit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=expense_account.id,
            debit_amount=amount,
            credit_amount=0.0,
            description=f"{sponsorship.sponsorship_category} - Direct sponsorship",
        )
        db.add(debit_line)

        # Credit: In-Kind Contribution Income (as per standard accounting practice)
        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=income_account.id,
            debit_amount=0.0,
            credit_amount=amount,
            description=f"In-Kind sponsorship - {sponsorship.sponsorship_category} (FMV: ₹{amount})",
        )
        db.add(credit_line)

        db.flush()
        return journal_entry

    except Exception as e:
        print(f"❌ Error posting direct vendor payment: {e}")
        return None


# ===== SPONSORSHIP CRUD =====


@router.post("/", response_model=SponsorshipResponse, status_code=status.HTTP_201_CREATED)
def create_sponsorship(
    sponsorship_data: SponsorshipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create new sponsorship
    """
    # Verify temple_id matches current user
    if sponsorship_data.temple_id != current_user.temple_id:
        raise HTTPException(
            status_code=403, detail="Cannot create sponsorship for different temple"
        )

    # Verify devotee exists
    devotee = (
        db.query(Devotee)
        .filter(
            Devotee.id == sponsorship_data.devotee_id, Devotee.temple_id == current_user.temple_id
        )
        .first()
    )

    if not devotee:
        raise HTTPException(status_code=404, detail="Devotee not found")

    # Verify vendor exists if direct payment mode
    if sponsorship_data.payment_mode == SponsorshipPaymentMode.DIRECT_PAYMENT:
        if not sponsorship_data.vendor_id:
            raise HTTPException(
                status_code=400, detail="Vendor ID required for direct payment mode"
            )

        vendor = (
            db.query(Vendor)
            .filter(
                Vendor.id == sponsorship_data.vendor_id, Vendor.temple_id == current_user.temple_id
            )
            .first()
        )

        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")

    # Generate receipt number first (before creating sponsorship)
    receipt_number = generate_sponsorship_receipt_number(db, current_user.temple_id)

    # Create sponsorship record
    sponsorship = Sponsorship(
        temple_id=sponsorship_data.temple_id,
        devotee_id=sponsorship_data.devotee_id,
        receipt_number=receipt_number,  # Set receipt number at creation
        receipt_date=sponsorship_data.receipt_date,
        sponsorship_category=sponsorship_data.sponsorship_category,
        description=sponsorship_data.description,
        committed_amount=sponsorship_data.committed_amount,
        payment_mode=sponsorship_data.payment_mode,
        event_name=sponsorship_data.event_name,
        event_date=sponsorship_data.event_date,
        vendor_id=sponsorship_data.vendor_id,
        vendor_invoice_number=sponsorship_data.vendor_invoice_number,
        vendor_invoice_date=sponsorship_data.vendor_invoice_date,
        vendor_invoice_amount=sponsorship_data.vendor_invoice_amount,
        vendor_invoice_document_url=sponsorship_data.vendor_invoice_document_url,
        status=SponsorshipStatus.COMMITTED,
    )

    db.add(sponsorship)
    db.flush()

    # Post to accounting based on payment mode
    if sponsorship_data.payment_mode == SponsorshipPaymentMode.TEMPLE_PAYMENT:
        # Temple payment mode: Post commitment (Dr. Receivable, Cr. Income)
        journal_entry = post_sponsorship_commitment(
            db, current_user.temple_id, sponsorship, current_user
        )
        if journal_entry:
            sponsorship.journal_entry_id_commitment = journal_entry.id
    elif sponsorship_data.payment_mode == SponsorshipPaymentMode.DIRECT_PAYMENT:
        # Direct payment mode: Post immediately if vendor invoice details provided
        # This follows standard accounting practice: Dr. Expense, Cr. In-Kind Income
        if sponsorship_data.vendor_invoice_amount and sponsorship_data.vendor_invoice_number:
            journal_entry = post_direct_payment_to_vendor(
                db, current_user.temple_id, sponsorship, current_user
            )
            if journal_entry:
                sponsorship.journal_entry_id_expense = journal_entry.id
                print(
                    f"✅ Posted direct payment sponsorship to accounting: Dr. Expense, Cr. In-Kind Income (₹{sponsorship_data.vendor_invoice_amount})"
                )
            else:
                print(
                    f"⚠️ Warning: Failed to post direct payment sponsorship to accounting. Check expense and income accounts exist."
                )

    db.commit()
    db.refresh(sponsorship)

    # Populate devotee and vendor names
    sponsorship.devotee_name = devotee.name
    if sponsorship.vendor:
        sponsorship.vendor_name = sponsorship.vendor.vendor_name

    return sponsorship


@router.get("/", response_model=List[SponsorshipResponse])
def list_sponsorships(
    status: Optional[SponsorshipStatus] = None,
    payment_mode: Optional[SponsorshipPaymentMode] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get list of sponsorships with filters
    """
    query = db.query(Sponsorship).filter(Sponsorship.temple_id == current_user.temple_id)

    if status:
        query = query.filter(Sponsorship.status == status)

    if payment_mode:
        query = query.filter(Sponsorship.payment_mode == payment_mode)

    if from_date:
        query = query.filter(func.date(Sponsorship.receipt_date) >= from_date)

    if to_date:
        query = query.filter(func.date(Sponsorship.receipt_date) <= to_date)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Sponsorship.sponsorship_category.ilike(search_filter))
            | (Sponsorship.description.ilike(search_filter))
            | (Sponsorship.receipt_number.ilike(search_filter))
        )

    sponsorships = query.order_by(Sponsorship.receipt_date.desc()).limit(limit).offset(offset).all()

    # Populate devotee and vendor names
    for sponsorship in sponsorships:
        if sponsorship.devotee:
            sponsorship.devotee_name = sponsorship.devotee.name
        if sponsorship.vendor:
            sponsorship.vendor_name = sponsorship.vendor.vendor_name

    return sponsorships


@router.get("/{sponsorship_id}", response_model=SponsorshipResponse)
def get_sponsorship(
    sponsorship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get sponsorship by ID
    """
    sponsorship = (
        db.query(Sponsorship)
        .filter(Sponsorship.id == sponsorship_id, Sponsorship.temple_id == current_user.temple_id)
        .first()
    )

    if not sponsorship:
        raise HTTPException(status_code=404, detail="Sponsorship not found")

    # Populate devotee and vendor names
    if sponsorship.devotee:
        sponsorship.devotee_name = sponsorship.devotee.name
    if sponsorship.vendor:
        sponsorship.vendor_name = sponsorship.vendor.vendor_name

    return sponsorship


@router.put("/{sponsorship_id}", response_model=SponsorshipResponse)
def update_sponsorship(
    sponsorship_id: int,
    sponsorship_data: SponsorshipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update sponsorship
    """
    sponsorship = (
        db.query(Sponsorship)
        .filter(Sponsorship.id == sponsorship_id, Sponsorship.temple_id == current_user.temple_id)
        .first()
    )

    if not sponsorship:
        raise HTTPException(status_code=404, detail="Sponsorship not found")

    # Update fields
    update_data = sponsorship_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sponsorship, field, value)

    sponsorship.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(sponsorship)

    # Populate devotee and vendor names
    if sponsorship.devotee:
        sponsorship.devotee_name = sponsorship.devotee.name
    if sponsorship.vendor:
        sponsorship.vendor_name = sponsorship.vendor.vendor_name

    return sponsorship


# ===== SPONSORSHIP PAYMENT (for temple_payment mode) =====


@router.post("/payment", response_model=SponsorshipPaymentResponse)
def record_sponsorship_payment(
    payment_data: SponsorshipPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Record payment for sponsorship (temple_payment mode only)
    """
    # Verify temple_id matches current user
    if payment_data.temple_id != current_user.temple_id:
        raise HTTPException(status_code=403, detail="Cannot record payment for different temple")

    # Get sponsorship
    sponsorship = (
        db.query(Sponsorship)
        .filter(
            Sponsorship.id == payment_data.sponsorship_id,
            Sponsorship.temple_id == current_user.temple_id,
        )
        .first()
    )

    if not sponsorship:
        raise HTTPException(status_code=404, detail="Sponsorship not found")

    # Verify payment mode is temple_payment
    if sponsorship.payment_mode != SponsorshipPaymentMode.TEMPLE_PAYMENT:
        raise HTTPException(
            status_code=400, detail="Cannot record payment for direct payment mode sponsorships"
        )

    # Check if payment exceeds committed amount
    if sponsorship.amount_paid + payment_data.amount_paid > sponsorship.committed_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Payment exceeds committed amount. Remaining: {sponsorship.committed_amount - sponsorship.amount_paid}",
        )

    # Create payment record
    payment = SponsorshipPayment(
        sponsorship_id=payment_data.sponsorship_id,
        temple_id=payment_data.temple_id,
        payment_date=payment_data.payment_date,
        amount_paid=payment_data.amount_paid,
        payment_method=payment_data.payment_method,
        transaction_reference=payment_data.transaction_reference,
    )
    db.add(payment)
    db.flush()

    # Update sponsorship amount_paid and status
    sponsorship.amount_paid += payment_data.amount_paid

    if sponsorship.amount_paid >= sponsorship.committed_amount:
        sponsorship.status = SponsorshipStatus.PAID
    elif sponsorship.amount_paid > 0:
        sponsorship.status = SponsorshipStatus.PARTIALLY_PAID

    # Post to accounting
    journal_entry = post_sponsorship_payment(
        db, current_user.temple_id, sponsorship, payment, current_user
    )
    if journal_entry:
        payment.journal_entry_id = journal_entry.id

    db.commit()
    db.refresh(payment)

    return payment


@router.get("/{sponsorship_id}/payments", response_model=List[SponsorshipPaymentResponse])
def get_sponsorship_payments(
    sponsorship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get payment history for a sponsorship
    """
    # Verify sponsorship exists and belongs to temple
    sponsorship = (
        db.query(Sponsorship)
        .filter(Sponsorship.id == sponsorship_id, Sponsorship.temple_id == current_user.temple_id)
        .first()
    )

    if not sponsorship:
        raise HTTPException(status_code=404, detail="Sponsorship not found")

    payments = (
        db.query(SponsorshipPayment)
        .filter(SponsorshipPayment.sponsorship_id == sponsorship_id)
        .order_by(SponsorshipPayment.payment_date.desc())
        .all()
    )

    return payments


# ===== DIRECT PAYMENT MODE =====


@router.post("/{sponsorship_id}/record-direct-payment", response_model=SponsorshipResponse)
def record_direct_vendor_payment(
    sponsorship_id: int,
    payment_data: DirectPaymentRecord,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Record that devotee paid vendor directly (for direct_payment mode)
    """
    sponsorship = (
        db.query(Sponsorship)
        .filter(Sponsorship.id == sponsorship_id, Sponsorship.temple_id == current_user.temple_id)
        .first()
    )

    if not sponsorship:
        raise HTTPException(status_code=404, detail="Sponsorship not found")

    # Verify payment mode is direct_payment
    if sponsorship.payment_mode != SponsorshipPaymentMode.DIRECT_PAYMENT:
        raise HTTPException(
            status_code=400, detail="This endpoint is only for direct payment mode sponsorships"
        )

    # Update vendor invoice details
    sponsorship.vendor_invoice_number = payment_data.vendor_invoice_number
    sponsorship.vendor_invoice_date = payment_data.vendor_invoice_date
    sponsorship.vendor_invoice_amount = payment_data.vendor_invoice_amount
    sponsorship.vendor_invoice_document_url = payment_data.vendor_invoice_document_url
    sponsorship.amount_paid = payment_data.vendor_invoice_amount
    sponsorship.status = SponsorshipStatus.PAID

    # Post to accounting (non-cash transaction)
    journal_entry = post_direct_payment_to_vendor(
        db, current_user.temple_id, sponsorship, current_user
    )
    if journal_entry:
        sponsorship.journal_entry_id_expense = journal_entry.id

    db.commit()
    db.refresh(sponsorship)

    # Populate devotee and vendor names
    if sponsorship.devotee:
        sponsorship.devotee_name = sponsorship.devotee.name
    if sponsorship.vendor:
        sponsorship.vendor_name = sponsorship.vendor.vendor_name

    return sponsorship


# ===== FULFILLMENT =====


@router.post("/{sponsorship_id}/fulfill", response_model=SponsorshipResponse)
def fulfill_sponsorship(
    sponsorship_id: int,
    fulfill_data: SponsorshipFulfill,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark sponsorship as fulfilled (service/event completed)
    """
    sponsorship = (
        db.query(Sponsorship)
        .filter(Sponsorship.id == sponsorship_id, Sponsorship.temple_id == current_user.temple_id)
        .first()
    )

    if not sponsorship:
        raise HTTPException(status_code=404, detail="Sponsorship not found")

    # Check if paid
    if sponsorship.status not in [SponsorshipStatus.PAID]:
        raise HTTPException(
            status_code=400, detail="Only paid sponsorships can be marked as fulfilled"
        )

    sponsorship.status = SponsorshipStatus.FULFILLED
    sponsorship.fulfilled_date = fulfill_data.fulfilled_date

    db.commit()
    db.refresh(sponsorship)

    # Populate devotee and vendor names
    if sponsorship.devotee:
        sponsorship.devotee_name = sponsorship.devotee.name
    if sponsorship.vendor:
        sponsorship.vendor_name = sponsorship.vendor.vendor_name

    return sponsorship
