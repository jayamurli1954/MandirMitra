"""
In-Kind Donation API Endpoints
Manage non-monetary donations like rice, gold, furniture, etc.
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
from app.models.inkind_sponsorship import (
    InKindDonation, InKindConsumption,
    InKindDonationType, InKindStatus
)
from app.models.accounting import Account, JournalEntry, JournalLine, JournalEntryStatus, TransactionType
from app.schemas.inkind import (
    InKindDonationCreate, InKindDonationUpdate, InKindDonationResponse,
    InKindConsumptionCreate, InKindConsumptionResponse,
    InventorySummary, InventoryItem
)

router = APIRouter(prefix="/api/v1/inkind-donations", tags=["inkind-donations"])


# ===== HELPER FUNCTIONS =====

def generate_inkind_receipt_number(db: Session, temple_id: int, donation_type: InKindDonationType) -> str:
    """
    Generate unique receipt number for in-kind donations
    """
    year = datetime.now().year

    # Get prefix based on donation type
    if donation_type == InKindDonationType.CONSUMABLE:
        prefix = f"INK-CON/{year}/"
    elif donation_type == InKindDonationType.PRECIOUS:
        prefix = f"INK-PRC/{year}/"
    elif donation_type == InKindDonationType.ASSET:
        prefix = f"INK-AST/{year}/"
    else:
        prefix = f"INK-GEN/{year}/"

    # Get last receipt number
    last_donation = db.query(InKindDonation).filter(
        InKindDonation.temple_id == temple_id,
        InKindDonation.receipt_number.like(f"{prefix}%")
    ).order_by(InKindDonation.id.desc()).first()

    if last_donation and last_donation.receipt_number:
        try:
            last_num = int(last_donation.receipt_number.split('/')[-1])
            new_num = last_num + 1
        except:
            new_num = 1
    else:
        new_num = 1

    return f"{prefix}{new_num:04d}"


def post_inkind_to_accounts(
    db: Session,
    temple_id: int,
    inkind_donation: InKindDonation,
    current_user: User
) -> Optional[JournalEntry]:
    """
    Post in-kind donation to accounting
    Dr. Inventory/Asset Account
       Cr. In-Kind Donation Income
    """
    try:
        # Get asset/inventory account based on type
        if inkind_donation.donation_type == InKindDonationType.CONSUMABLE:
            # Inventory - Consumables
            asset_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == "1201",  # Inventory - Consumables
                Account.is_active == True
            ).first()
        elif inkind_donation.donation_type == InKindDonationType.PRECIOUS:
            # Precious Items Inventory
            asset_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == "1202",  # Inventory - Precious Items
                Account.is_active == True
            ).first()
        elif inkind_donation.donation_type == InKindDonationType.ASSET:
            # Fixed Assets
            asset_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code.like("130%"),  # Fixed Assets
                Account.is_active == True
            ).first()
        else:
            # General Inventory
            asset_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == "1203",  # Inventory - General
                Account.is_active == True
            ).first()

        if not asset_account:
            print(f"⚠️ Warning: No asset account found for {inkind_donation.donation_type}")
            return None

        # Get income account - In-Kind Donations
        income_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == "4103",  # Donation - In-Kind
            Account.is_active == True
        ).first()

        if not income_account:
            print(f"⚠️ Warning: No in-kind donation income account found")
            return None

        # Generate entry number
        entry_number = f"JE/{datetime.now().year}/{inkind_donation.id:04d}"

        # Create journal entry
        narration = f"In-Kind Donation - {inkind_donation.item_name}"
        if inkind_donation.devotee:
            narration += f" from {inkind_donation.devotee.name}"

        journal_entry = JournalEntry(
            entry_number=entry_number,
            entry_date=inkind_donation.receipt_date,
            narration=narration,
            reference_type=TransactionType.INKIND_DONATION,
            reference_id=inkind_donation.id,
            temple_id=temple_id,
            total_amount=inkind_donation.value_assessed,
            status=JournalEntryStatus.POSTED,
            created_by=current_user.id,
            posted_by=current_user.id,
            posted_at=datetime.utcnow()
        )
        db.add(journal_entry)
        db.flush()

        # Debit: Asset/Inventory Account
        debit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=asset_account.id,
            debit_amount=inkind_donation.value_assessed,
            credit_amount=0.0,
            description=f"{inkind_donation.item_name} - {inkind_donation.quantity} {inkind_donation.unit}"
        )
        db.add(debit_line)

        # Credit: In-Kind Donation Income
        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=income_account.id,
            debit_amount=0.0,
            credit_amount=inkind_donation.value_assessed,
            description=f"In-Kind donation - {inkind_donation.item_name}"
        )
        db.add(credit_line)

        db.flush()
        return journal_entry

    except Exception as e:
        print(f"❌ Error posting in-kind donation to accounts: {e}")
        return None


def post_consumption_to_accounts(
    db: Session,
    temple_id: int,
    consumption: InKindConsumption,
    inkind_donation: InKindDonation,
    current_user: User
) -> Optional[JournalEntry]:
    """
    Post consumption to accounting
    Dr. Expense Account (based on purpose)
       Cr. Inventory Account
    """
    try:
        # Get inventory account
        if inkind_donation.donation_type == InKindDonationType.CONSUMABLE:
            inventory_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == "1201",  # Inventory - Consumables
                Account.is_active == True
            ).first()

            # Get expense account - typically Annadana Expenses
            expense_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code.like("530%"),  # Annadana/Prasada Expenses
                Account.is_active == True
            ).first()
        else:
            # Other types rarely consumed, but handle anyway
            inventory_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == "1203",  # Inventory - General
                Account.is_active == True
            ).first()

            expense_account = db.query(Account).filter(
                Account.temple_id == temple_id,
                Account.account_code == "5000",  # General Temple Operations
                Account.is_active == True
            ).first()

        if not inventory_account or not expense_account:
            print(f"⚠️ Warning: Missing accounts for consumption posting")
            return None

        # Calculate value consumed (proportional to quantity)
        if inkind_donation.quantity > 0:
            value_consumed = (consumption.quantity_consumed / inkind_donation.quantity) * inkind_donation.value_assessed
        else:
            value_consumed = 0.0

        # Generate entry number
        entry_number = f"JE/{datetime.now().year}/C{consumption.id:04d}"

        # Create journal entry
        narration = f"Consumption of {inkind_donation.item_name} - {consumption.purpose or 'General Use'}"

        journal_entry = JournalEntry(
            entry_number=entry_number,
            entry_date=consumption.consumption_date,
            narration=narration,
            reference_type=TransactionType.INKIND_CONSUMPTION,
            reference_id=consumption.id,
            temple_id=temple_id,
            total_amount=value_consumed,
            status=JournalEntryStatus.POSTED,
            created_by=current_user.id,
            posted_by=current_user.id,
            posted_at=datetime.utcnow()
        )
        db.add(journal_entry)
        db.flush()

        # Debit: Expense Account
        debit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=expense_account.id,
            debit_amount=value_consumed,
            credit_amount=0.0,
            description=f"{consumption.quantity_consumed} {inkind_donation.unit} of {inkind_donation.item_name}"
        )
        db.add(debit_line)

        # Credit: Inventory Account
        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=inventory_account.id,
            debit_amount=0.0,
            credit_amount=value_consumed,
            description=f"Consumed from stock"
        )
        db.add(credit_line)

        db.flush()
        return journal_entry

    except Exception as e:
        print(f"❌ Error posting consumption to accounts: {e}")
        return None


# ===== IN-KIND DONATION CRUD =====

@router.post("/", response_model=InKindDonationResponse)
def create_inkind_donation(
    donation_data: InKindDonationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new in-kind donation
    """
    # Verify temple_id matches current user
    if donation_data.temple_id != current_user.temple_id:
        raise HTTPException(status_code=403, detail="Cannot create donation for different temple")

    # Verify devotee exists
    devotee = db.query(Devotee).filter(
        Devotee.id == donation_data.devotee_id,
        Devotee.temple_id == current_user.temple_id
    ).first()

    if not devotee:
        raise HTTPException(status_code=404, detail="Devotee not found")

    # Create in-kind donation record
    inkind_donation = InKindDonation(
        temple_id=donation_data.temple_id,
        devotee_id=donation_data.devotee_id,
        receipt_date=donation_data.receipt_date,
        donation_type=donation_data.donation_type,
        item_name=donation_data.item_name,
        item_category=donation_data.item_category,
        item_description=donation_data.item_description,
        quantity=donation_data.quantity,
        unit=donation_data.unit,
        value_assessed=donation_data.value_assessed,
        value_per_unit=donation_data.value_per_unit,
        purpose=donation_data.purpose,
        purity=donation_data.purity,
        weight_gross=donation_data.weight_gross,
        weight_net=donation_data.weight_net,
        appraised_by=donation_data.appraised_by,
        appraisal_date=donation_data.appraisal_date,
        photo_url=donation_data.photo_url,
        document_url=donation_data.document_url,
        status=InKindStatus.RECEIVED
    )

    # For consumables, set current balance to quantity
    if donation_data.donation_type == InKindDonationType.CONSUMABLE:
        inkind_donation.current_balance = donation_data.quantity
        inkind_donation.status = InKindStatus.IN_STOCK

    db.add(inkind_donation)
    db.flush()

    # Generate receipt number
    receipt_number = generate_inkind_receipt_number(db, current_user.temple_id, donation_data.donation_type)
    inkind_donation.receipt_number = receipt_number

    # Post to accounting
    journal_entry = post_inkind_to_accounts(db, current_user.temple_id, inkind_donation, current_user)
    if journal_entry:
        inkind_donation.journal_entry_id = journal_entry.id

    db.commit()
    db.refresh(inkind_donation)

    # Populate devotee name
    inkind_donation.devotee_name = devotee.name

    return inkind_donation


@router.get("/", response_model=List[InKindDonationResponse])
def list_inkind_donations(
    donation_type: Optional[InKindDonationType] = None,
    status: Optional[InKindStatus] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of in-kind donations with filters
    """
    query = db.query(InKindDonation).filter(
        InKindDonation.temple_id == current_user.temple_id
    )

    if donation_type:
        query = query.filter(InKindDonation.donation_type == donation_type)

    if status:
        query = query.filter(InKindDonation.status == status)

    if from_date:
        query = query.filter(func.date(InKindDonation.receipt_date) >= from_date)

    if to_date:
        query = query.filter(func.date(InKindDonation.receipt_date) <= to_date)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (InKindDonation.item_name.ilike(search_filter)) |
            (InKindDonation.item_category.ilike(search_filter)) |
            (InKindDonation.receipt_number.ilike(search_filter))
        )

    donations = query.order_by(InKindDonation.receipt_date.desc()).limit(limit).offset(offset).all()

    # Populate devotee names
    for donation in donations:
        if donation.devotee:
            donation.devotee_name = donation.devotee.name

    return donations


@router.get("/{donation_id}", response_model=InKindDonationResponse)
def get_inkind_donation(
    donation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get in-kind donation by ID
    """
    donation = db.query(InKindDonation).filter(
        InKindDonation.id == donation_id,
        InKindDonation.temple_id == current_user.temple_id
    ).first()

    if not donation:
        raise HTTPException(status_code=404, detail="In-kind donation not found")

    # Populate devotee name
    if donation.devotee:
        donation.devotee_name = donation.devotee.name

    return donation


@router.put("/{donation_id}", response_model=InKindDonationResponse)
def update_inkind_donation(
    donation_id: int,
    donation_data: InKindDonationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update in-kind donation
    """
    donation = db.query(InKindDonation).filter(
        InKindDonation.id == donation_id,
        InKindDonation.temple_id == current_user.temple_id
    ).first()

    if not donation:
        raise HTTPException(status_code=404, detail="In-kind donation not found")

    # Update fields
    update_data = donation_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(donation, field, value)

    donation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(donation)

    # Populate devotee name
    if donation.devotee:
        donation.devotee_name = donation.devotee.name

    return donation


# ===== CONSUMPTION TRACKING =====

@router.post("/consumption", response_model=InKindConsumptionResponse)
def record_consumption(
    consumption_data: InKindConsumptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record consumption of in-kind donation (mainly for consumables)
    """
    # Verify temple_id matches current user
    if consumption_data.temple_id != current_user.temple_id:
        raise HTTPException(status_code=403, detail="Cannot record consumption for different temple")

    # Get in-kind donation
    inkind_donation = db.query(InKindDonation).filter(
        InKindDonation.id == consumption_data.inkind_donation_id,
        InKindDonation.temple_id == current_user.temple_id
    ).first()

    if not inkind_donation:
        raise HTTPException(status_code=404, detail="In-kind donation not found")

    # Check if enough balance available
    if inkind_donation.current_balance < consumption_data.quantity_consumed:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Available: {inkind_donation.current_balance} {inkind_donation.unit}"
        )

    # Create consumption record
    consumption = InKindConsumption(
        inkind_donation_id=consumption_data.inkind_donation_id,
        temple_id=consumption_data.temple_id,
        consumption_date=consumption_data.consumption_date,
        quantity_consumed=consumption_data.quantity_consumed,
        purpose=consumption_data.purpose,
        event_name=consumption_data.event_name,
        event_date=consumption_data.event_date
    )
    db.add(consumption)
    db.flush()

    # Update in-kind donation balance
    inkind_donation.current_balance -= consumption_data.quantity_consumed
    inkind_donation.consumed_quantity += consumption_data.quantity_consumed

    # Update status if fully consumed
    if inkind_donation.current_balance <= 0:
        inkind_donation.status = InKindStatus.CONSUMED

    # Post to accounting
    journal_entry = post_consumption_to_accounts(
        db, current_user.temple_id, consumption, inkind_donation, current_user
    )
    if journal_entry:
        consumption.journal_entry_id = journal_entry.id

    db.commit()
    db.refresh(consumption)

    return consumption


@router.get("/consumption/history/{donation_id}", response_model=List[InKindConsumptionResponse])
def get_consumption_history(
    donation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get consumption history for a specific in-kind donation
    """
    # Verify donation exists and belongs to temple
    donation = db.query(InKindDonation).filter(
        InKindDonation.id == donation_id,
        InKindDonation.temple_id == current_user.temple_id
    ).first()

    if not donation:
        raise HTTPException(status_code=404, detail="In-kind donation not found")

    consumptions = db.query(InKindConsumption).filter(
        InKindConsumption.inkind_donation_id == donation_id
    ).order_by(InKindConsumption.consumption_date.desc()).all()

    return consumptions


# ===== INVENTORY REPORTS =====

@router.get("/inventory/summary", response_model=List[InventorySummary])
def get_inventory_summary(
    donation_type: Optional[InKindDonationType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get inventory summary grouped by donation type and item category
    """
    query = db.query(InKindDonation).filter(
        InKindDonation.temple_id == current_user.temple_id,
        InKindDonation.status.in_([InKindStatus.RECEIVED, InKindStatus.IN_STOCK, InKindStatus.IN_USE])
    )

    if donation_type:
        query = query.filter(InKindDonation.donation_type == donation_type)

    donations = query.all()

    # Group by donation type and item category
    summaries = []
    grouped = {}

    for donation in donations:
        dtype = donation.donation_type
        if dtype not in grouped:
            grouped[dtype] = {}

        category = donation.item_category or "General"
        if category not in grouped[dtype]:
            grouped[dtype][category] = {
                "item_name": donation.item_name,
                "item_category": category,
                "total_quantity": 0.0,
                "consumed_quantity": 0.0,
                "current_balance": 0.0,
                "unit": donation.unit,
                "total_value": 0.0,
                "donation_count": 0
            }

        grouped[dtype][category]["total_quantity"] += donation.quantity
        grouped[dtype][category]["consumed_quantity"] += donation.consumed_quantity
        grouped[dtype][category]["current_balance"] += donation.current_balance
        grouped[dtype][category]["total_value"] += donation.value_assessed
        grouped[dtype][category]["donation_count"] += 1

    # Convert to response format
    for dtype, categories in grouped.items():
        items = [InventoryItem(**item_data) for item_data in categories.values()]
        total_value = sum(item.total_value for item in items)

        summaries.append(InventorySummary(
            donation_type=dtype,
            items=items,
            total_value=total_value,
            total_items=len(items)
        ))

    return summaries
