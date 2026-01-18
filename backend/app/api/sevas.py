"""
Seva API Endpoints
Handles temple sevas/poojas/archanas
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel
import io

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.auto_setup import is_standalone_mode
from app.models.user import User
from app.models.seva import Seva, SevaBooking, SevaCategory, SevaAvailability, SevaBookingStatus
from app.models.devotee import Devotee
from app.models.temple import Temple
from app.models.accounting import (
    Account,
    JournalEntry,
    JournalLine,
    JournalEntryStatus,
    TransactionType,
)
from app.schemas.seva import (
    SevaCreate,
    SevaUpdate,
    SevaResponse,
    SevaListResponse,
    SevaBookingCreate,
    SevaBookingUpdate,
    SevaBookingResponse,
)
from app.services.printer import get_print_queue
from app.constants.hindu_constants import GOTHRAS, NAKSHATRAS, RASHIS

router = APIRouter(prefix="/api/v1/sevas", tags=["sevas"])


def _parse_except_days(seva) -> Optional[List[int]]:
    """
    Helper function to parse except_days from seva object.
    Returns list of excluded day numbers, or None if not set.
    """
    if not hasattr(seva, "except_days") or not seva.except_days:
        return None

    import json

    if isinstance(seva.except_days, str):
        try:
            return json.loads(seva.except_days)
        except json.JSONDecodeError:
            return None
    elif isinstance(seva.except_days, list):
        return seva.except_days
    return None


def get_seva_safely(db: Session, seva_id: int = None, filter_conditions: dict = None):
    """
    Safely query Seva model, handling missing columns (materials_required, except_days)
    Returns Seva object or None (single) or list of Seva objects
    """
    from sqlalchemy import text

    # Check which optional columns exist
    from app.core.database import column_exists
    
    def check_column_exists(column_name: str) -> bool:
        """Check if a column exists in sevas table"""
        return column_exists(db, "sevas", column_name)

    has_materials_column = check_column_exists("materials_required")
    has_except_days_column = check_column_exists("except_days")

    if not has_materials_column or not has_except_days_column:
        # Use raw SQL - only select columns that exist
        sql = """
            SELECT id, name_english, name_kannada, name_sanskrit, description, category,
                   amount, min_amount, max_amount, availability, specific_day, except_day"""

        # Add except_days if it exists
        if has_except_days_column:
            sql += ", except_days"

        sql += """,
                   time_slot, max_bookings_per_day, advance_booking_days, requires_approval,
                   is_active, is_token_seva, token_color, token_threshold, account_id,
                   benefits, instructions, duration_minutes, created_at, updated_at
            FROM sevas
            WHERE 1=1
        """
        params = {}

        if seva_id:
            sql += " AND id = :seva_id"
            params["seva_id"] = seva_id

        if filter_conditions:
            for key, value in filter_conditions.items():
                sql += f" AND {key} = :{key}"
                params[key] = value

        result = db.execute(text(sql), params)
        rows = result.fetchall()

        if not rows:
            return None if seva_id else []

        class SevaProxy:
            def __init__(self, row_data, has_except_days_col):
                idx = 0
                self.id = row_data[idx]
                idx += 1
                self.name_english = row_data[idx]
                idx += 1
                self.name_kannada = row_data[idx]
                idx += 1
                self.name_sanskrit = row_data[idx]
                idx += 1
                self.description = row_data[idx]
                idx += 1
                self.category = row_data[idx]
                idx += 1
                self.amount = row_data[idx]
                idx += 1
                self.min_amount = row_data[idx]
                idx += 1
                self.max_amount = row_data[idx]
                idx += 1
                self.availability = row_data[idx]
                idx += 1
                self.specific_day = row_data[idx]
                idx += 1
                self.except_day = row_data[idx]
                idx += 1
                # Handle except_days column if it exists
                if has_except_days_col:
                    self.except_days = row_data[idx]
                    idx += 1
                else:
                    self.except_days = None
                self.time_slot = row_data[idx]
                idx += 1
                self.max_bookings_per_day = row_data[idx]
                idx += 1
                self.advance_booking_days = row_data[idx]
                idx += 1
                self.requires_approval = row_data[idx]
                idx += 1
                self.is_active = row_data[idx]
                idx += 1
                self.is_token_seva = row_data[idx]
                idx += 1
                self.token_color = row_data[idx]
                idx += 1
                self.token_threshold = row_data[idx]
                idx += 1
                self.account_id = row_data[idx]
                idx += 1
                self.benefits = row_data[idx]
                idx += 1
                self.instructions = row_data[idx]
                idx += 1
                self.duration_minutes = row_data[idx]
                idx += 1
                self.created_at = row_data[idx]
                idx += 1
                self.updated_at = row_data[idx]
                idx += 1
                self.materials_required = None

        if seva_id:
            return SevaProxy(rows[0], has_except_days_column) if rows else None
        else:
            return [SevaProxy(r, has_except_days_column) for r in rows]
    else:
        # Use normal ORM
        query = db.query(Seva)
        if seva_id:
            query = query.filter(Seva.id == seva_id)
        if filter_conditions:
            for key, value in filter_conditions.items():
                query = query.filter(getattr(Seva, key) == value)
        return query.first() if seva_id else query.all()


def post_seva_to_accounting(db: Session, booking: SevaBooking, temple_id: int):
    """
    Create journal entry for seva booking in accounting system

    Two dates are tracked:
    1. Receipt Date: System-generated (booking.created_at.date()) - date when booking was confirmed
    2. Booking Date: User-entered (booking.booking_date) - date when seva will be performed

    Accounting Rules:
    - If booking_date == today: Dr Cash/Bank, Cr Seva Income (3002) - immediate income
    - If booking_date > today: Dr Cash/Bank, Cr Advance Seva Booking (3003) - liability until seva date

    The advance booking (3003) will be automatically transferred to Seva Income (3002)
    on the morning of the booking_date via daily batch transfer.
    """
    try:
        # Determine debit account (payment method) using helper function
        from app.core.bank_account_helper import (
            get_bank_account_for_payment,
            get_cash_account_for_payment,
        )

        payment_method = booking.payment_method or "CASH"
        payment_method_upper = payment_method.upper()

        if payment_method_upper in ["CASH", "COUNTER"]:
            debit_account = get_cash_account_for_payment(
                db, temple_id, payment_method_upper, hundi=False
            )
            if not debit_account:
                # Fallback to hardcoded code if helper doesn't find account
                debit_account = (
                    db.query(Account)
                    .filter(
                        Account.temple_id == temple_id,
                        Account.account_code == "11001",  # Cash in Hand - Counter
                    )
                    .first()
                )
        elif payment_method_upper in [
            "UPI",
            "ONLINE",
            "CARD",
            "NETBANKING",
            "BANK",
            "CHEQUE",
            "DD",
        ]:
            # Get bank account from BankAccount model
            debit_account, fallback_code = get_bank_account_for_payment(
                db,
                temple_id,
                payment_method_upper,
                bank_account_id=getattr(booking, "bank_account_id", None),
            )
            if not debit_account and fallback_code:
                debit_account = (
                    db.query(Account)
                    .filter(Account.temple_id == temple_id, Account.account_code == fallback_code)
                    .first()
                )
            if not debit_account:
                print(
                    f"  WARNING: No bank account found for payment method {payment_method}. Please create a bank account in Bank Account Management."
                )
        else:
            # Default to cash counter
            debit_account = get_cash_account_for_payment(
                db, temple_id, payment_method_upper, hundi=False
            )
            if not debit_account:
                debit_account = (
                    db.query(Account)
                    .filter(Account.temple_id == temple_id, Account.account_code == "11001")
                    .first()
                )

        # Check if this is an advance booking
        # Receipt date = booking.created_at.date() (system-generated, cannot be changed)
        # Booking date = booking.booking_date (user-entered, when seva will be performed)
        today = date.today()
        is_advance_booking = booking.booking_date > today  # Future date = advance booking

        # Determine credit account
        credit_account = None

        if is_advance_booking:
            # For advance bookings, always credit Advance Seva Booking (21003)
            credit_account_code = "21003"  # Advance Seva Booking
            credit_account = (
                db.query(Account)
                .filter(Account.temple_id == temple_id, Account.account_code == credit_account_code)
                .first()
            )

            if credit_account:
                print(
                    f"  Using advance seva booking account: {credit_account.account_code} - {credit_account.account_name}"
                )
            else:
                print(
                    f"  ERROR: Advance Seva Booking account {credit_account_code} not found. Please create '21003 - Advance Seva Booking' in Chart of Accounts."
                )
        else:
            # For same-day or past bookings, use seva-linked account or default to 3002
            # First, try to use seva-linked account
            if booking.seva and hasattr(booking.seva, "account_id") and booking.seva.account_id:
                credit_account = (
                    db.query(Account).filter(Account.id == booking.seva.account_id).first()
                )

            # Fallback: Use 42002 - Seva Income (General) as default
            if not credit_account:
                credit_account_code = "42002"  # Seva Income - General
                credit_account = (
                    db.query(Account)
                    .filter(
                        Account.temple_id == temple_id, Account.account_code == credit_account_code
                    )
                    .first()
                )

                if credit_account:
                    print(
                        f"  Using default seva income account: {credit_account.account_code} - {credit_account.account_name}"
                    )
                else:
                    print(
                        f"  ERROR: Default seva income account {credit_account_code} not found. Please ensure '42002 - Seva Income - General' exists in Chart of Accounts."
                    )

        if not debit_account:
            error_msg = f"Debit account ({debit_account_code}) not found for temple {temple_id}. Please create the account in Chart of Accounts."
            raise ValueError(error_msg)

        if not credit_account:
            if is_advance_booking:
                error_msg = f"Advance Seva Booking account (3003) not found for temple {temple_id}. Please create '3003 - Advance Seva Booking' in Chart of Accounts."
            else:
                error_msg = f"Credit account not found for seva '{booking.seva.name_english if booking.seva else 'Unknown'}'. Please link an account to the seva or create default seva income account (account code 3002)."
            raise ValueError(error_msg)

        # Create narration
        devotee_name = booking.devotee.name if booking.devotee else "Unknown"
        seva_name = booking.seva.name_english if booking.seva else "Seva"
        receipt_date = (
            booking.created_at.date()
            if hasattr(booking, "created_at") and booking.created_at
            else today
        )
        if is_advance_booking:
            narration = f"Advance seva booking - {seva_name} by {devotee_name} (Receipt: {receipt_date.strftime('%d-%m-%Y')}, Seva date: {booking.booking_date.strftime('%d-%m-%Y')})"
        else:
            narration = f"Seva booking - {seva_name} by {devotee_name} (Seva date: {booking.booking_date.strftime('%d-%m-%Y')})"

        # Generate entry number first
        year = booking.booking_date.year
        prefix = f"JE/{year}/"

        # Get last entry number for this year
        # Use load_only to avoid integrity_hash column if it doesn't exist
        from sqlalchemy.orm import load_only

        last_entry = (
            db.query(JournalEntry)
            .options(load_only(JournalEntry.id, JournalEntry.entry_number, JournalEntry.temple_id))
            .filter(
                JournalEntry.temple_id == temple_id, JournalEntry.entry_number.like(f"{prefix}%")
            )
            .order_by(JournalEntry.id.desc())
            .first()
        )

        if last_entry:
            # Extract number and increment
            try:
                last_num = int(last_entry.entry_number.split("/")[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1

        entry_number = f"{prefix}{new_num:04d}"

        # Entry date should be receipt date (when money was received), not booking date
        # Receipt date = booking.created_at.date() (system-generated, cannot be changed)
        # Booking date = booking.booking_date (user-entered, when seva will be performed)
        receipt_date = (
            booking.created_at.date() if hasattr(booking.created_at, "date") else booking.created_at
        )
        if isinstance(receipt_date, date):
            entry_date = datetime.combine(receipt_date, datetime.min.time())
        else:
            # Fallback to today if receipt_date is not available
            entry_date = datetime.combine(today, datetime.min.time())

        # Create journal entry
        # Note: created_by is required, so use booking.user_id or default to 1
        created_by = booking.user_id if booking.user_id else 1

        journal_entry = JournalEntry(
            temple_id=temple_id,
            entry_date=entry_date,
            entry_number=entry_number,
            narration=narration,
            reference_type=TransactionType.SEVA,
            reference_id=booking.id,
            total_amount=booking.amount_paid,
            status=JournalEntryStatus.POSTED,
            created_by=created_by,
            posted_by=created_by,
            posted_at=datetime.utcnow(),
        )
        db.add(journal_entry)
        db.flush()  # Get journal_entry.id

        # Create journal lines
        # Debit: Payment Account (Cash/Bank increases)
        debit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=debit_account.id,
            debit_amount=booking.amount_paid,
            credit_amount=0,
            description=f"Seva booking received via {payment_method}",
        )

        # Credit: Seva Income (Income increases)
        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=credit_account.id,
            debit_amount=0,
            credit_amount=booking.amount_paid,
            description=f"Seva income - {seva_name}",
        )

        db.add(debit_line)
        db.add(credit_line)

        return journal_entry

    except Exception as e:
        print(f"Error posting seva to accounting: {str(e)}")
        raise e


# ===== SEVA MANAGEMENT =====


@router.get("/", response_model=List[SevaListResponse])
def list_sevas(
    category: Optional[SevaCategory] = None,
    is_active: bool = True,
    include_inactive: bool = False,
    for_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """List all sevas with availability check"""
    from sqlalchemy import text

    try:
        print(
            f"Fetching sevas: category={category}, is_active={is_active}, include_inactive={include_inactive}, for_date={for_date}"
        )
    except Exception as e:
        print(f"Error in list_sevas: {str(e)}")
        import traceback

        traceback.print_exc()
        return []

    # Use ORM query directly - handle missing except_days column gracefully
    try:
        query = db.query(Seva)

        if not include_inactive:
            query = query.filter(Seva.is_active == is_active)

        if category:
            query = query.filter(Seva.category == category)

        sevas = query.all()

    except Exception as e:
        error_str = str(e)
        # Check if error is due to missing except_days column
        if "except_days" in error_str and (
            "does not exist" in error_str or "UndefinedColumn" in error_str
        ):
            print(f"Warning: except_days column not found, using get_seva_safely fallback")
            try:
                db.rollback()
                # Fallback to get_seva_safely which handles missing columns
                filter_conditions = {}
                if not include_inactive:
                    filter_conditions["is_active"] = is_active
                if category:
                    filter_conditions["category"] = (
                        category.value if hasattr(category, "value") else str(category)
                    )
                sevas = get_seva_safely(db, filter_conditions=filter_conditions)
                if sevas is None:
                    sevas = []
            except Exception as fallback_error:
                print(f"Error in fallback query: {str(fallback_error)}")
                import traceback

                traceback.print_exc()
                db.rollback()
                return []
        else:
            print(f"Error in list_sevas query: {str(e)}")
            import traceback

            traceback.print_exc()
            # Rollback transaction on error
            try:
                db.rollback()
            except:
                pass
            return []

    # Add availability check for specific date
    check_date = for_date or date.today()
    day_of_week = check_date.weekday()  # 0=Monday, 6=Sunday
    # Convert to our format (0=Sunday, 6=Saturday)
    day_of_week = (day_of_week + 1) % 7

    # Helper function to normalize enum values
    def normalize_enum(value):
        """Convert enum or string to lowercase string"""
        if value is None:
            return None
        if hasattr(value, "value"):
            # It's an enum object
            return value.value.lower()
        # It's a string (from raw SQL query)
        return str(value).lower() if value else None

    result = []
    for seva in sevas:
        try:
            # Normalize enum values for Pydantic schema
            category_value = normalize_enum(seva.category)
            availability_value = normalize_enum(seva.availability)

            # Ensure required fields have valid values
            if not category_value:
                category_value = "special"  # Default category
            if not availability_value:
                availability_value = "daily"  # Default availability

            # Check availability for today
            availability_str = availability_value
            is_available = True
            if availability_str == "specific_day":
                is_available = (
                    (day_of_week == seva.specific_day) if seva.specific_day is not None else True
                )
            elif availability_str == "except_day":
                # Check multiple excluded days (except_days) or single excluded day (except_day for backward compatibility)
                except_days_list = []
                if hasattr(seva, "except_days") and seva.except_days:
                    import json

                    if isinstance(seva.except_days, str):
                        try:
                            except_days_list = json.loads(seva.except_days)
                        except json.JSONDecodeError:
                            except_days_list = []
                    elif isinstance(seva.except_days, list):
                        except_days_list = seva.except_days
                # Also check legacy except_day field for backward compatibility
                if (
                    hasattr(seva, "except_day")
                    and seva.except_day is not None
                    and seva.except_day not in except_days_list
                ):
                    except_days_list.append(seva.except_day)

                is_available = day_of_week not in except_days_list if except_days_list else True
            elif availability_str == "weekday":
                is_available = day_of_week >= 1 and day_of_week <= 5
            elif availability_str == "weekend":
                is_available = day_of_week == 0 or day_of_week == 6

            # Check booking availability
            bookings_available = None
            if seva.max_bookings_per_day:
                bookings_count = (
                    db.query(SevaBooking)
                    .filter(
                        SevaBooking.seva_id == seva.id,
                        SevaBooking.booking_date == check_date,
                        SevaBooking.status.in_(
                            [SevaBookingStatus.PENDING, SevaBookingStatus.CONFIRMED]
                        ),
                    )
                    .count()
                )
                bookings_available = max(0, seva.max_bookings_per_day - bookings_count)

            # Create response object
            seva_response = SevaListResponse(
                id=seva.id,
                name_english=seva.name_english or "",
                name_kannada=seva.name_kannada,
                name_sanskrit=seva.name_sanskrit,
                description=seva.description,
                category=category_value,
                amount=float(seva.amount) if seva.amount is not None else 0.0,
                min_amount=float(seva.min_amount) if seva.min_amount is not None else None,
                max_amount=float(seva.max_amount) if seva.max_amount is not None else None,
                availability=availability_value,
                specific_day=seva.specific_day,
                except_day=seva.except_day,
                except_days=_parse_except_days(seva),
                time_slot=seva.time_slot,
                is_active=bool(seva.is_active),
                is_available_today=is_available,
                bookings_available=bookings_available,
            )

            result.append(seva_response)
        except Exception as e:
            print(f"Error processing seva {seva.id}: {str(e)}")
            import traceback

            traceback.print_exc()
            # Skip this seva and continue with others
            continue

    return result


# ===== DROPDOWN OPTIONS (Must be before /{seva_id} route) =====


@router.get("/dropdown-options")
def get_dropdown_options():
    """Get dropdown options for Gothra, Nakshatra, and Rashi"""
    try:
        return {"gothras": GOTHRAS, "nakshatras": NAKSHATRAS, "rashis": RASHIS}
    except Exception as e:
        print(f"Error in dropdown-options endpoint: {e}")
        # Return empty arrays as fallback
        return {"gothras": [], "nakshatras": [], "rashis": []}


@router.get("/{seva_id}", response_model=SevaResponse)
def get_seva(seva_id: int, db: Session = Depends(get_db)):
    """Get seva details"""
    seva = get_seva_safely(db, seva_id=seva_id)
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found")
    return seva


@router.post("/", response_model=SevaResponse)
def create_seva(
    seva_data: SevaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    """Create new seva (admin/temple_manager only)"""
    if current_user.role not in ["admin", "temple_manager"] and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Only admins and temple managers can create sevas"
        )

    # Filter out materials_required if it exists (column may not exist in database)
    seva_dict = seva_data.dict()
    seva_dict.pop("materials_required", None)  # Remove if present

    # Convert except_days list to JSON string for storage
    if "except_days" in seva_dict and seva_dict["except_days"] is not None:
        import json

        if isinstance(seva_dict["except_days"], list):
            seva_dict["except_days"] = json.dumps(seva_dict["except_days"])

    seva = Seva(**seva_dict)
    seva.temple_id = current_user.temple_id if current_user else None
    db.add(seva)
    db.flush()  # Get seva.id for audit log

    # Create audit log
    try:
        from app.core.audit import log_action, get_entity_dict

        log_action(
            db=db,
            user=current_user,
            action="CREATE",
            entity_type="Seva",
            entity_id=seva.id,
            new_values=get_entity_dict(seva),
            description=f"Created seva: {seva.name_english}",
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
        )
    except Exception as e:
        print(f"Warning: Failed to create audit log: {e}")
        # Don't fail seva creation if audit log fails

    db.commit()
    db.refresh(seva)
    return seva


@router.put("/{seva_id}", response_model=SevaResponse)
def update_seva(
    seva_id: int,
    seva_data: SevaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    """Update seva (admin/temple_manager only)"""
    if current_user.role not in ["admin", "temple_manager"] and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Only admins and temple managers can update sevas"
        )

    # For updates we MUST use the real SQLAlchemy model instance, not the SevaProxy
    # returned by get_seva_safely (which is meant only for read scenarios where
    # the materials_required column might be missing).
    seva = db.query(Seva).filter(Seva.id == seva_id).first()
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found")

    # Update fields (exclude materials_required as it may not exist in the model)
    # Use model_dump() for Pydantic v2, fallback to dict() for v1
    try:
        update_data = seva_data.model_dump(exclude_unset=True)
    except AttributeError:
        # Fallback for Pydantic v1
        update_data = seva_data.dict(exclude_unset=True)
    update_data.pop("materials_required", None)  # Remove if present

    # Convert except_days list to JSON string for storage
    if "except_days" in update_data and update_data["except_days"] is not None:
        import json

        # Handle both list and string inputs (frontend might send string)
        if isinstance(update_data["except_days"], list):
            update_data["except_days"] = json.dumps(update_data["except_days"])
        elif isinstance(update_data["except_days"], str):
            # If it's already a JSON string, validate it's valid JSON
            try:
                # Validate it's valid JSON, but keep as string for storage
                json.loads(update_data["except_days"])
                # It's already a valid JSON string, keep it
            except json.JSONDecodeError:
                # Invalid JSON string, try to parse as array literal
                try:
                    # Try to parse as Python list literal (e.g., "[1, 6]")
                    parsed = eval(update_data["except_days"])
                    if isinstance(parsed, list):
                        update_data["except_days"] = json.dumps(parsed)
                    else:
                        update_data["except_days"] = None
                except:
                    update_data["except_days"] = None

    # Debug logging - use print to ensure it shows in console
    print(f"🔍 Update data for seva {seva_id}: {update_data}")
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"Update data for seva {seva_id}: {update_data}")

    # Get old values for audit log before updating
    try:
        from app.core.audit import log_action, get_entity_dict

        old_values = get_entity_dict(seva) if hasattr(seva, "__table__") else {}
    except Exception:
        old_values = {}

    for key, value in update_data.items():
        # Handle enum fields - The TypeDecorator will handle conversion
        # Just ensure we pass the enum object or its value, TypeDecorator will normalize it
        if key == "category":
            try:
                # Convert to enum object if it's a string - TypeDecorator will handle the rest
                if isinstance(value, SevaCategory):
                    # Already an enum, TypeDecorator will extract .value
                    pass
                else:
                    # Validate and convert to enum - TypeDecorator will use .value
                    value = SevaCategory(value)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid category: {value}. Valid categories are: {[cat.value for cat in SevaCategory]}",
                )
        elif key == "availability":
            # Handle availability enum similarly
            if not isinstance(value, SevaAvailability):
                value = SevaAvailability(value)

        try:
            setattr(seva, key, value)
            print(f"✅ Set {key} = {value} (type: {type(value)})")
        except Exception as e:
            error_msg = f"❌ Error setting {key} to {value}: {str(e)}"
            print(error_msg)
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=f"Error updating field {key}: {str(e)}")

    seva.updated_at = datetime.utcnow()

    try:
        db.flush()
        print(f"✅ Successfully flushed seva {seva_id} to database")
    except Exception as e:
        db.rollback()
        error_msg = f"❌ Database error updating seva {seva_id}: {str(e)}"
        print(error_msg)
        import traceback

        traceback.print_exc()
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Failed to update seva: {str(e)}")

    # Create audit log
    try:
        from app.core.audit import log_action, get_entity_dict

        new_values = get_entity_dict(seva) if hasattr(seva, "__table__") else {}
        log_action(
            db=db,
            user=current_user,
            action="UPDATE",
            entity_type="Seva",
            entity_id=seva.id,
            old_values=old_values,
            new_values=new_values,
            description=f"Updated seva: {seva.name_english}",
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
        )
    except Exception as e:
        print(f"Warning: Failed to create audit log: {e}")
        # Don't fail seva update if audit log fails

    db.commit()
    db.refresh(seva)
    return seva


@router.delete("/{seva_id}")
def delete_seva(
    seva_id: int,
    reason: Optional[str] = Query(None, description="Reason for deletion (required)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    """Delete seva (soft delete by marking inactive)

    Requirements:
    - Admin/Temple Manager approval required
    - Cannot delete if there are future bookings
    - Reason must be provided
    """
    if current_user.role not in ["admin", "temple_manager"] and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Only admins and temple managers can delete sevas"
        )

    if not reason or not reason.strip():
        raise HTTPException(
            status_code=400,
            detail="Reason for deletion is required. Please provide a reason for audit trail.",
        )

    seva = get_seva_safely(db, seva_id=seva_id)
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found")

    # Check for future bookings
    future_bookings = (
        db.query(SevaBooking)
        .filter(
            SevaBooking.seva_id == seva_id,
            SevaBooking.booking_date >= date.today(),
            SevaBooking.status.in_([SevaBookingStatus.PENDING, SevaBookingStatus.CONFIRMED]),
        )
        .count()
    )

    if future_bookings > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete seva. There are {future_bookings} future booking(s). Please cancel or complete all future bookings first.",
        )

    # Get old values for audit log
    old_values = get_entity_dict(seva) if hasattr(seva, "__table__") else {}

    # Soft delete by marking inactive
    seva.is_active = False
    seva.updated_at = datetime.utcnow()
    db.flush()

    # Create audit log with reason
    try:
        from app.core.audit import log_action, get_entity_dict

        new_values = get_entity_dict(seva) if hasattr(seva, "__table__") else {}
        log_action(
            db=db,
            user=current_user,
            action="DELETE",
            entity_type="Seva",
            entity_id=seva.id,
            old_values=old_values,
            new_values=new_values,
            description=f"Deleted seva: {seva.name_english}. Reason: {reason}",
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
        )
    except Exception as e:
        print(f"Warning: Failed to create audit log: {e}")
        # Don't fail seva deletion if audit log fails

    db.commit()
    return {"message": "Seva deleted successfully"}


# ===== SEVA AVAILABILITY & BOOKING HELPERS =====


@router.get("/{seva_id}/available-dates")
def get_available_dates(
    seva_id: int,
    weeks_ahead: int = Query(12, ge=1, le=52, description="Number of weeks to look ahead"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get available booking dates for a seva

    Returns list of dates with:
    - Date
    - Day of week
    - Available slots (max_bookings_per_day - current_bookings)
    - Is available (boolean)
    """
    seva = get_seva_safely(db, seva_id=seva_id)
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found")

    if not seva.is_active:
        raise HTTPException(status_code=400, detail="Seva is not active")

    # Normalize availability
    availability_str = str(seva.availability).lower()
    if hasattr(seva.availability, "value"):
        availability_str = seva.availability.value.lower()

    # Calculate date range
    start_date = date.today()
    end_date = start_date + timedelta(weeks=weeks_ahead)

    available_dates = []
    current_date = start_date

    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    while current_date <= end_date:
        day_of_week = (current_date.weekday() + 1) % 7  # 0=Sunday, 6=Saturday

        # Check if seva is available on this day
        is_available_day = True
        if availability_str == "specific_day":
            is_available_day = day_of_week == seva.specific_day
        elif availability_str == "except_day":
            # Check multiple excluded days (except_days) or single excluded day (except_day for backward compatibility)
            except_days_list = []
            if hasattr(seva, "except_days") and seva.except_days:
                import json

                if isinstance(seva.except_days, str):
                    try:
                        except_days_list = json.loads(seva.except_days)
                    except json.JSONDecodeError:
                        except_days_list = []
                elif isinstance(seva.except_days, list):
                    except_days_list = seva.except_days
            # Also check legacy except_day field for backward compatibility
            if (
                hasattr(seva, "except_day")
                and seva.except_day is not None
                and seva.except_day not in except_days_list
            ):
                except_days_list.append(seva.except_day)

            is_available_day = day_of_week not in except_days_list if except_days_list else True
        elif availability_str == "weekday":
            is_available_day = day_of_week >= 1 and day_of_week <= 5
        elif availability_str == "weekend":
            is_available_day = day_of_week == 0 or day_of_week == 6
        # 'daily' and 'festival_only' are always available (subject to max bookings)

        if is_available_day:
            # Check advance booking limit (only if advance_booking_days is set)
            days_ahead = (current_date - start_date).days
            if seva.advance_booking_days is None or days_ahead <= seva.advance_booking_days:
                # Count existing bookings for this date
                existing_bookings = (
                    db.query(SevaBooking)
                    .filter(
                        SevaBooking.seva_id == seva_id,
                        SevaBooking.booking_date == current_date,
                        SevaBooking.status.in_(
                            [SevaBookingStatus.PENDING, SevaBookingStatus.CONFIRMED]
                        ),
                    )
                    .count()
                )

                max_bookings = seva.max_bookings_per_day if seva.max_bookings_per_day else 999
                available_slots = max(0, max_bookings - existing_bookings)
                is_available = available_slots > 0

                available_dates.append(
                    {
                        "date": current_date.isoformat(),
                        "day_of_week": day_names[day_of_week],
                        "day_number": day_of_week,
                        "available_slots": available_slots,
                        "max_slots": max_bookings,
                        "booked_slots": existing_bookings,
                        "is_available": is_available,
                        "time_slot": seva.time_slot,
                    }
                )

        current_date += timedelta(days=1)

    return {
        "seva_id": seva_id,
        "seva_name": seva.name_english,
        "availability_type": availability_str,
        "specific_day": seva.specific_day,
        "max_bookings_per_day": seva.max_bookings_per_day,
        "advance_booking_days": seva.advance_booking_days,
        "available_dates": available_dates,
    }


# ===== SEVA BOOKINGS =====


def serialize_booking_response(booking: SevaBooking) -> dict:
    """
    Helper function to serialize a SevaBooking with relationships to dict
    """
    response_data = {
        "id": booking.id,
        "seva_id": booking.seva_id,
        "devotee_id": booking.devotee_id,
        "user_id": booking.user_id,
        "priest_id": booking.priest_id,
        "booking_date": booking.booking_date,
        "booking_time": booking.booking_time,
        "status": booking.status.value if hasattr(booking.status, "value") else str(booking.status),
        "amount_paid": booking.amount_paid,
        "payment_method": booking.payment_method,
        "payment_reference": booking.payment_reference,
        "receipt_number": booking.receipt_number,
        "devotee_names": booking.devotee_names,
        "gotra": booking.gotra,
        "nakshatra": booking.nakshatra,
        "rashi": booking.rashi,
        "special_request": booking.special_request,
        "admin_notes": booking.admin_notes,
        "completed_at": booking.completed_at,
        "cancelled_at": booking.cancelled_at,
        "cancellation_reason": booking.cancellation_reason,
        "original_booking_date": booking.original_booking_date,
        "reschedule_requested_date": booking.reschedule_requested_date,
        "reschedule_reason": booking.reschedule_reason,
        "reschedule_approved": booking.reschedule_approved,
        "reschedule_approved_by": booking.reschedule_approved_by,
        "reschedule_approved_at": booking.reschedule_approved_at,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at,
    }

    # Serialize seva relationship - convert to dict for Pydantic v2 compatibility
    if booking.seva:
        try:
            # Convert to SevaResponse first, then to dict
            if hasattr(SevaResponse, "from_orm"):
                seva_obj = SevaResponse.from_orm(booking.seva)
                response_data["seva"] = (
                    seva_obj.dict() if hasattr(seva_obj, "dict") else seva_obj.model_dump()
                )
            else:
                seva_obj = SevaResponse.model_validate(booking.seva)
                response_data["seva"] = (
                    seva_obj.model_dump() if hasattr(seva_obj, "model_dump") else dict(seva_obj)
                )
        except Exception as e:
            print(f"Error serializing seva: {e}")
            # Fallback to manual dict construction
            response_data["seva"] = {
                "id": booking.seva.id,
                "name_english": booking.seva.name_english,
                "name_kannada": getattr(booking.seva, "name_kannada", None),
                "name_sanskrit": getattr(booking.seva, "name_sanskrit", None),
                "category": str(booking.seva.category)
                if hasattr(booking.seva, "category")
                else None,
                "amount": booking.seva.amount,
            }
    else:
        response_data["seva"] = None

    # Serialize devotee relationship as dict
    if booking.devotee:
        response_data["devotee"] = {
            "id": booking.devotee.id,
            "name": booking.devotee.name,
            "phone": booking.devotee.phone,
            "email": getattr(booking.devotee, "email", None),
        }
    else:
        response_data["devotee"] = None

    # Serialize priest relationship as dict (if exists)
    if booking.priest:
        response_data["priest"] = {
            "id": booking.priest.id,
            "name": getattr(booking.priest, "name", None)
            or getattr(booking.priest, "full_name", None),
            "email": getattr(booking.priest, "email", None),
        }
    else:
        response_data["priest"] = None

    return response_data


@router.get("/bookings/", response_model=List[SevaBookingResponse])
def list_bookings(
    seva_id: Optional[int] = None,
    devotee_id: Optional[int] = None,
    booking_date: Optional[date] = None,
    status: Optional[SevaBookingStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List seva bookings"""
    query = db.query(SevaBooking).options(
        joinedload(SevaBooking.seva),
        joinedload(SevaBooking.devotee),
        joinedload(SevaBooking.priest),
    )

    # Non-admin users can only see their own bookings
    if current_user.role != "admin":
        query = query.filter(SevaBooking.user_id == current_user.id)

    if seva_id:
        query = query.filter(SevaBooking.seva_id == seva_id)
    if devotee_id:
        query = query.filter(SevaBooking.devotee_id == devotee_id)
    if booking_date:
        query = query.filter(SevaBooking.booking_date == booking_date)
    if status:
        query = query.filter(SevaBooking.status == status)

    bookings = query.offset(skip).limit(limit).all()

    # Serialize each booking properly
    return [SevaBookingResponse(**serialize_booking_response(booking)) for booking in bookings]


@router.get("/bookings/{booking_id}", response_model=SevaBookingResponse)
def get_booking(
    booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get booking details"""
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check permissions
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")

    return booking


@router.post("/bookings/", response_model=SevaBookingResponse)
def create_booking(
    booking_data: SevaBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new seva booking"""
    # Validate seva exists and is active
    seva = get_seva_safely(db, seva_id=booking_data.seva_id, filter_conditions={"is_active": True})
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found or inactive")

    # Check advance booking limit (only if advance_booking_days is set)
    if seva.advance_booking_days is not None and seva.advance_booking_days > 0:
        max_date = date.today() + timedelta(days=seva.advance_booking_days)
        if booking_data.booking_date > max_date:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot book more than {seva.advance_booking_days} days in advance",
            )

    # Check availability for the day
    day_of_week = (booking_data.booking_date.weekday() + 1) % 7
    if seva.availability == SevaAvailability.SPECIFIC_DAY and day_of_week != seva.specific_day:
        raise HTTPException(status_code=400, detail="Seva not available on this day")
    elif seva.availability == SevaAvailability.EXCEPT_DAY:
        # Check multiple excluded days (except_days) or single excluded day (except_day for backward compatibility)
        except_days_list = []
        if seva.except_days:
            # Parse JSON string to list if it's stored as string
            import json

            if isinstance(seva.except_days, str):
                try:
                    except_days_list = json.loads(seva.except_days)
                except json.JSONDecodeError:
                    except_days_list = []
            elif isinstance(seva.except_days, list):
                except_days_list = seva.except_days
        # Also check legacy except_day field for backward compatibility
        if seva.except_day is not None and seva.except_day not in except_days_list:
            except_days_list.append(seva.except_day)

        if day_of_week in except_days_list:
            # Get day names for better error message
            day_names = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ]
            excluded_day_names = [day_names[d] for d in except_days_list]
            raise HTTPException(
                status_code=400,
                detail=f"Seva not available on {day_names[day_of_week]}. This seva is not performed on: {', '.join(excluded_day_names)}",
            )

    # Check max bookings per day
    if seva.max_bookings_per_day:
        existing_bookings = (
            db.query(SevaBooking)
            .filter(
                SevaBooking.seva_id == seva.id,
                SevaBooking.booking_date == booking_data.booking_date,
                SevaBooking.status.in_([SevaBookingStatus.PENDING, SevaBookingStatus.CONFIRMED]),
            )
            .count()
        )

        if existing_bookings >= seva.max_bookings_per_day:
            available_slots = seva.max_bookings_per_day - existing_bookings
            raise HTTPException(
                status_code=400,
                detail=f"No slots available for this date. Maximum {seva.max_bookings_per_day} booking(s) allowed per day. Already booked: {existing_bookings}/{seva.max_bookings_per_day}",
            )

    # Generate receipt number - sequential serial number format (SEV000001, SEV000002, etc.)
    # In standalone mode, use simple "SEV" prefix (no temple-specific prefix needed)
    receipt_prefix = "SEV"

    # Filter by receipt prefix pattern
    # In standalone mode, don't filter by temple (single temple environment)
    # In multi-tenant mode, filter through seva relationship if needed
    booking_filter = [
        SevaBooking.receipt_number.isnot(None),
        SevaBooking.receipt_number.like(f"{receipt_prefix}%"),
    ]

    # In multi-tenant mode, filter by temple through seva relationship
    if not is_standalone_mode() and current_user.temple_id:
        seva_ids = db.query(Seva.id).filter(Seva.temple_id == current_user.temple_id).all()
        if seva_ids:
            seva_id_list = [s[0] for s in seva_ids]
            booking_filter.append(SevaBooking.seva_id.in_(seva_id_list))

    last_booking = (
        db.query(SevaBooking).filter(and_(*booking_filter)).order_by(SevaBooking.id.desc()).first()
    )

    if last_booking and last_booking.receipt_number:
        # Extract the number part from the last receipt (e.g., SEV000001 -> 1, SEV000123 -> 123)
        try:
            last_num_str = last_booking.receipt_number.replace("SEV", "").strip()
            # Handle both old format (timestamp-based like SEV202512180951133) and new format (serial like SEV000001)
            if (
                last_num_str.isdigit() and len(last_num_str) <= 6
            ):  # Simple serial number (SEV000001 to SEV999999)
                last_num = int(last_num_str)
            elif (
                last_num_str.isdigit() and len(last_num_str) > 10
            ):  # Old timestamp format - use booking ID
                # For old format, use the maximum booking ID + 1 to continue sequence
                max_booking = db.query(SevaBooking).order_by(SevaBooking.id.desc()).first()
                last_num = max_booking.id if max_booking else 0
            else:
                # Fallback to booking ID
                last_num = last_booking.id
            new_num = last_num + 1
        except (ValueError, AttributeError):
            # Fallback: use count of bookings + 1
            new_num = (db.query(SevaBooking).count() or 0) + 1
    else:
        new_num = 1

    receipt_number = f"{receipt_prefix}{str(new_num).zfill(6)}"  # SEV000001, SEV000002, etc.

    # Create booking (but don't commit yet - wait for accounting)
    try:
        booking = SevaBooking(
            **booking_data.dict(),
            user_id=current_user.id,
            status=SevaBookingStatus.PENDING
            if seva.requires_approval
            else SevaBookingStatus.CONFIRMED,
            receipt_number=receipt_number,
        )

        db.add(booking)
        db.flush()  # Flush to get booking.id, but don't commit yet
        db.refresh(booking)
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating seva booking: {str(e)}")
        print(f"   Booking data: {booking_data.dict()}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")

    # Post to accounting system BEFORE final commit
    # This ensures strict double-entry accounting - if accounting fails, booking fails
    if current_user and current_user.temple_id:
        try:
            journal_entry = post_seva_to_accounting(db, booking, current_user.temple_id)
            # No commit here - part of main transaction
        except Exception as e:
            # Accounting failed, so we must rollback the entire transaction
            db.rollback()
            print(f"Failed to post Seva to accounting: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Accounting Entry Failed: {str(e)}. Please correct the Chart of Accounts.",
            )

    # Only commit if accounting succeeded
    db.commit()
    db.refresh(booking)

    # Auto-send SMS/Email confirmation (if enabled and devotee preferences allow)
    try:
        if booking.devotee and booking.devotee.receive_sms and booking.devotee.phone:
            # Send SMS booking confirmation (async - don't block response)
            # TODO: Implement SMS service integration
            pass
        if booking.devotee and booking.devotee.receive_email and booking.devotee.email:
            # Send Email booking confirmation (async - don't block response)
            # TODO: Implement Email service integration
            pass
    except Exception as e:
        # Don't fail booking creation if SMS/Email fails
        print(f"Failed to send booking confirmation: {str(e)}")

    # Refresh to get relationships
    db.refresh(booking)

    # Use helper function to serialize booking
    return SevaBookingResponse(**serialize_booking_response(booking))


@router.put("/bookings/{booking_id}", response_model=SevaBookingResponse)
def update_booking(
    booking_id: int,
    booking_data: SevaBookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update booking"""
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check permissions
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this booking")

    for key, value in booking_data.dict(exclude_unset=True).items():
        setattr(booking, key, value)

    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking


@router.delete("/bookings/{booking_id}")
def cancel_booking(
    booking_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel booking"""
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check permissions
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")

    booking.status = SevaBookingStatus.CANCELLED
    booking.cancelled_at = datetime.utcnow()
    booking.cancellation_reason = reason
    db.commit()

    # Auto-send SMS/Email notification (if enabled and devotee preferences allow)
    try:
        if booking.devotee and booking.devotee.receive_sms and booking.devotee.phone:
            # Send SMS cancellation notification (async - don't block response)
            # TODO: Implement SMS service integration
            pass
        if booking.devotee and booking.devotee.receive_email and booking.devotee.email:
            # Send Email cancellation notification (async - don't block response)
            # TODO: Implement Email service integration
            pass
    except Exception as e:
        # Don't fail cancellation if SMS/Email fails
        print(f"Failed to send cancellation notification: {str(e)}")

    return {"message": "Booking cancelled successfully"}


# ===== SEVA RESCHEDULE (POSTPONE/PREPONE) =====


@router.put("/bookings/{booking_id}/reschedule")
def request_reschedule(
    booking_id: int,
    new_date: date = Query(..., description="New booking date"),
    reason: str = Query(..., description="Reason for reschedule"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Request to reschedule (postpone/prepone) a seva booking
    Requires admin approval

    Business Rules:
    - Can reschedule bookings for today or future dates
    - Cannot reschedule bookings from previous days (already completed)
    - Advance bookings can be rescheduled until the seva date
    """
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check permissions - user can request reschedule for their own bookings
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reschedule this booking")

    # Check if booking is from a previous day (already completed - cannot reschedule)
    today = date.today()
    if booking.booking_date < today:
        raise HTTPException(
            status_code=400,
            detail="Cannot reschedule a completed seva. Only today's and future bookings can be rescheduled.",
        )

    # Validate new date
    if new_date == booking.booking_date:
        raise HTTPException(status_code=400, detail="New date must be different from current date")

    # Store original date if not already stored
    if not booking.original_booking_date:
        booking.original_booking_date = booking.booking_date

    # Set reschedule request
    booking.reschedule_requested_date = new_date
    booking.reschedule_reason = reason
    booking.reschedule_approved = None  # Pending approval

    db.commit()
    db.refresh(booking)

    return {
        "message": "Reschedule request submitted. Waiting for admin approval.",
        "booking_id": booking.id,
        "original_date": booking.original_booking_date,
        "requested_date": new_date,
        "status": "pending_approval",
    }


@router.get("/bookings/pending-reschedule", response_model=List[SevaBookingResponse])
def get_pending_reschedule_requests(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get all pending reschedule requests (admin/temple_manager only)
    """
    # Note: Default admin user has role="temple_manager", so we allow both
    if current_user.role not in ["admin", "temple_manager"] and not getattr(
        current_user, "is_superuser", False
    ):
        raise HTTPException(
            status_code=403,
            detail="Only admins and temple managers can view pending reschedule requests",
        )

    # Get bookings with pending reschedule requests (reschedule_approved IS NULL and reschedule_requested_date IS NOT NULL)
    bookings = (
        db.query(SevaBooking)
        .options(
            joinedload(SevaBooking.seva),
            joinedload(SevaBooking.devotee),
            joinedload(SevaBooking.priest),
        )
        .filter(
            SevaBooking.reschedule_approved.is_(None),
            SevaBooking.reschedule_requested_date.isnot(None),
        )
        .all()
    )

    # Serialize each booking properly
    return [SevaBookingResponse(**serialize_booking_response(booking)) for booking in bookings]


@router.post("/bookings/{booking_id}/approve-reschedule")
def approve_reschedule(
    booking_id: int,
    approve: bool = Query(..., description="Approve (true) or reject (false)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Approve or reject a reschedule request (admin only)
    """
    # Check permissions - allow admin, temple_manager, and superusers
    # Note: Default admin user has role="temple_manager", so we allow both
    allowed_roles = ["admin", "temple_manager"]
    is_superuser = getattr(current_user, "is_superuser", False)

    if current_user.role not in allowed_roles and not is_superuser:
        raise HTTPException(
            status_code=403,
            detail=f"Only admins and temple managers can approve reschedule requests. Current role: {current_user.role}",
        )

    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.reschedule_approved is not None:
        raise HTTPException(status_code=400, detail="Reschedule request already processed")

    if not booking.reschedule_requested_date:
        raise HTTPException(status_code=400, detail="No reschedule request found")

    if approve:
        # Approve: Update booking date
        booking.booking_date = booking.reschedule_requested_date
        booking.reschedule_approved = True
        booking.reschedule_approved_by = current_user.id
        booking.reschedule_approved_at = datetime.utcnow()

        db.commit()
        return {
            "message": "Reschedule approved. Booking date updated.",
            "new_date": booking.booking_date,
            "original_date": booking.original_booking_date,
        }
    else:
        # Reject: Clear reschedule request
        booking.reschedule_approved = False
        booking.reschedule_approved_by = current_user.id
        booking.reschedule_approved_at = datetime.utcnow()

        db.commit()
    return {
        "message": "Reschedule request rejected.",
        "booking_date": booking.booking_date,  # Unchanged
    }


# ===== PRIEST ASSIGNMENT =====


@router.get("/priests")
def get_priests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get list of priests (users with role 'priest')"""
    priests = db.query(User).filter(User.role == "priest", User.is_active == True)

    # Filter by temple if in multi-tenant mode
    if current_user.temple_id:
        priests = priests.filter(User.temple_id == current_user.temple_id)

    priests = priests.all()

    return [{"id": p.id, "name": p.full_name, "email": p.email, "phone": p.phone} for p in priests]


@router.put("/bookings/{booking_id}/assign-priest")
def assign_priest(
    booking_id: int,
    priest_id: int = Query(..., description="Priest user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Assign a priest to a seva booking
    Only admins or staff can assign priests
    """
    # Check permissions
    if current_user.role not in ["admin", "temple_manager", "staff"]:
        raise HTTPException(status_code=403, detail="Only admins and staff can assign priests")

    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Verify priest exists and is active
    priest = (
        db.query(User)
        .filter(User.id == priest_id, User.role == "priest", User.is_active == True)
        .first()
    )

    if not priest:
        raise HTTPException(status_code=404, detail="Priest not found or inactive")

    # Assign priest
    booking.priest_id = priest_id
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)

    return {
        "message": f"Priest {priest.full_name} assigned successfully",
        "booking": SevaBookingResponse.from_orm(booking),
    }


@router.put("/bookings/{booking_id}/remove-priest")
def remove_priest(
    booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Remove priest assignment from a seva booking
    Only admins or staff can remove priest assignments
    """
    # Check permissions
    if current_user.role not in ["admin", "temple_manager", "staff"]:
        raise HTTPException(
            status_code=403, detail="Only admins and staff can remove priest assignments"
        )

    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.priest_id = None
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)

    return {
        "message": "Priest assignment removed successfully",
        "booking": SevaBookingResponse.from_orm(booking),
    }


@router.post("/bookings/{booking_id}/process-refund", response_model=dict)
def process_refund(
    booking_id: int,
    refund_amount: Optional[float] = Query(
        None, description="Refund amount (default: 90% of booking amount)"
    ),
    refund_method: str = Query(
        "original", description="Refund method: original, cash, bank_transfer"
    ),
    refund_reference: Optional[str] = Query(None, description="Transaction reference for refund"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Process refund for a cancelled booking
    Business rule: 90% refund (10% processing fee)
    Only admins or accountants can process refunds
    """
    # Check permissions
    if current_user.role not in ["admin", "accountant", "temple_manager"]:
        raise HTTPException(
            status_code=403, detail="Only admins and accountants can process refunds"
        )

    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status != SevaBookingStatus.CANCELLED:
        raise HTTPException(
            status_code=400, detail="Booking must be cancelled before processing refund"
        )

    # Check if refund already processed
    if hasattr(booking, "refund_processed") and booking.refund_processed:
        raise HTTPException(status_code=400, detail="Refund already processed for this booking")

    # Calculate refund amount (90% of booking amount, 10% processing fee)
    if refund_amount is None:
        refund_amount = booking.amount_paid * 0.9  # 90% refund
    else:
        # Validate refund amount doesn't exceed booking amount
        if refund_amount > booking.amount_paid:
            raise HTTPException(
                status_code=400, detail="Refund amount cannot exceed booking amount"
            )

    processing_fee = booking.amount_paid - refund_amount

    # Create refund record (add refund fields to booking model if not exists)
    # For now, store in admin_notes or create separate refund table
    refund_note = f"Refund processed: ₹{refund_amount:.2f} via {refund_method}. Processing fee: ₹{processing_fee:.2f}. Reference: {refund_reference or 'N/A'}"

    if booking.admin_notes:
        booking.admin_notes += f"\n{refund_note}"
    else:
        booking.admin_notes = refund_note

    # Mark refund as processed (if field exists)
    if hasattr(booking, "refund_processed"):
        booking.refund_processed = True
    if hasattr(booking, "refund_amount"):
        booking.refund_amount = refund_amount
    if hasattr(booking, "refund_method"):
        booking.refund_method = refund_method
    if hasattr(booking, "refund_reference"):
        booking.refund_reference = refund_reference
    if hasattr(booking, "refund_processed_at"):
        booking.refund_processed_at = datetime.utcnow()
    if hasattr(booking, "refund_processed_by"):
        booking.refund_processed_by = current_user.id

    # Create accounting entry for refund
    # Dr: Seva Income (reversal), Cr: Cash/Bank (refund payment)
    temple_id = current_user.temple_id if current_user else None
    if temple_id:
        try:
            # Get seva income account
            seva = booking.seva
            credit_account = None
            if seva and hasattr(seva, "account_id") and seva.account_id:
                credit_account = db.query(Account).filter(Account.id == seva.account_id).first()

            if not credit_account:
                credit_account_code = "42002"  # Seva Income - General
                credit_account = (
                    db.query(Account)
                    .filter(
                        Account.temple_id == temple_id, Account.account_code == credit_account_code
                    )
                    .first()
                )

            # Get debit account (refund payment method)
            debit_account_code = None
            if refund_method.upper() in ["CASH", "COUNTER"]:
                debit_account_code = "11001"  # Cash in Hand - Counter
            elif refund_method.upper() in ["BANK_TRANSFER", "ONLINE"]:
                debit_account_code = "12001"  # Bank Account
            else:
                debit_account_code = "11001"  # Default to cash

            debit_account = (
                db.query(Account)
                .filter(Account.temple_id == temple_id, Account.account_code == debit_account_code)
                .first()
            )

            if debit_account and credit_account:
                # Generate entry number
                year = datetime.now().year
                prefix = f"JE/{year}/"
                from sqlalchemy.orm import load_only

                last_entry = (
                    db.query(JournalEntry)
                    .options(
                        load_only(
                            JournalEntry.id, JournalEntry.entry_number, JournalEntry.temple_id
                        )
                    )
                    .filter(
                        JournalEntry.temple_id == temple_id,
                        JournalEntry.entry_number.like(f"{prefix}%"),
                    )
                    .order_by(JournalEntry.id.desc())
                    .first()
                )

                if last_entry:
                    try:
                        last_num = int(last_entry.entry_number.split("/")[-1])
                        new_num = last_num + 1
                    except:
                        new_num = 1
                else:
                    new_num = 1

                entry_number = f"{prefix}{new_num:04d}"

                # Create journal entry for refund
                refund_entry = JournalEntry(
                    temple_id=temple_id,
                    entry_date=datetime.now().date(),
                    entry_number=entry_number,
                    narration=f"Refund for booking {booking.receipt_number} - {seva.name_english if seva else 'Seva'}",
                    reference_type=TransactionType.SEVA_BOOKING,
                    reference_id=booking.id,
                    total_amount=refund_amount,
                    status=JournalEntryStatus.POSTED,
                    created_by=current_user.id,
                    posted_by=current_user.id,
                    posted_at=datetime.utcnow(),
                )
                db.add(refund_entry)
                db.flush()

                # Create journal lines
                # Dr: Seva Income (reversal - reduce income)
                db.add(
                    JournalLine(
                        journal_entry_id=refund_entry.id,
                        account_id=credit_account.id,
                        debit_amount=refund_amount,
                        credit_amount=0,
                        description=f"Refund reversal for booking {booking.receipt_number}",
                    )
                )

                # Cr: Cash/Bank (refund payment)
                db.add(
                    JournalLine(
                        journal_entry_id=refund_entry.id,
                        account_id=debit_account.id,
                        debit_amount=0,
                        credit_amount=refund_amount,
                        description=f"Refund payment for booking {booking.receipt_number}",
                    )
                )

                db.commit()
        except Exception as e:
            print(f"Failed to create refund accounting entry: {str(e)}")
            # Don't fail refund if accounting fails

    db.commit()
    db.refresh(booking)

    return {
        "message": "Refund processed successfully",
        "refund_amount": refund_amount,
        "processing_fee": processing_fee,
        "booking": SevaBookingResponse.from_orm(booking),
    }


@router.get("/bookings/{booking_id}/refund-status", response_model=dict)
def get_refund_status(
    booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get refund status for a cancelled booking"""
    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    refund_processed = hasattr(booking, "refund_processed") and booking.refund_processed
    refund_amount = getattr(booking, "refund_amount", None)
    refund_method = getattr(booking, "refund_method", None)
    refund_reference = getattr(booking, "refund_reference", None)

    # Calculate expected refund (90% of booking amount)
    expected_refund = booking.amount_paid * 0.9
    processing_fee = booking.amount_paid * 0.1

    return {
        "booking_id": booking.id,
        "receipt_number": booking.receipt_number,
        "booking_amount": booking.amount_paid,
        "expected_refund": expected_refund,
        "processing_fee": processing_fee,
        "refund_processed": refund_processed,
        "refund_amount": refund_amount,
        "refund_method": refund_method,
        "refund_reference": refund_reference,
        "refund_processed_at": getattr(booking, "refund_processed_at", None),
        "is_cancelled": booking.status == SevaBookingStatus.CANCELLED,
    }


def _number_to_words(n):
    """Convert number to words (simple implementation)"""
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    teens = [
        "Ten",
        "Eleven",
        "Twelve",
        "Thirteen",
        "Fourteen",
        "Fifteen",
        "Sixteen",
        "Seventeen",
        "Eighteen",
        "Nineteen",
    ]

    if n == 0:
        return "Zero"

    def convert_hundreds(num):
        result = ""
        if num >= 100:
            result += ones[num // 100] + " Hundred "
            num %= 100
        if num >= 20:
            result += tens[num // 10] + " "
            num %= 10
        elif num >= 10:
            result += teens[num - 10] + " "
            return result
        if num > 0:
            result += ones[num] + " "
        return result

    result = ""
    if n >= 10000000:  # Crores
        result += convert_hundreds(n // 10000000) + "Crore "
        n %= 10000000
    if n >= 100000:  # Lakhs
        result += convert_hundreds(n // 100000) + "Lakh "
        n %= 100000
    if n >= 1000:  # Thousands
        result += convert_hundreds(n // 1000) + "Thousand "
        n %= 1000
    if n > 0:
        result += convert_hundreds(n)

    return result.strip()


def _generate_seva_receipt_pdf(booking: SevaBooking, db: Session, temple_id: int = None):
    """
    Helper function to generate PDF receipt buffer for a seva booking
    Similar to donation receipts but customized for seva bookings
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    import requests
    import os

    # Get temple info
    temple = None
    temple_logo_path = None
    # Get temple_id from parameter, or from booking's devotee/user
    if not temple_id:
        if booking.devotee and hasattr(booking.devotee, "temple_id"):
            temple_id = booking.devotee.temple_id
        elif booking.user and hasattr(booking.user, "temple_id"):
            temple_id = booking.user.temple_id

    if temple_id:
        temple = db.query(Temple).filter(Temple.id == temple_id).first()
        if temple and temple.logo_url:
            try:
                if temple.logo_url.startswith("http"):
                    response = requests.get(temple.logo_url, timeout=5)
                    if response.status_code == 200:
                        temple_logo_path = io.BytesIO(response.content)
                elif os.path.exists(temple.logo_url):
                    temple_logo_path = temple.logo_url
            except:
                temple_logo_path = None

    # Get devotee and seva info
    devotee = booking.devotee if hasattr(booking, "devotee") else None
    seva = booking.seva if hasattr(booking, "seva") else None

    # Ensure seva is loaded - if not, try to load it
    if not seva and hasattr(booking, "seva_id") and booking.seva_id:
        from app.models.seva import Seva

        seva = db.query(Seva).filter(Seva.id == booking.seva_id).first()

    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    elements = []

    styles = getSampleStyleSheet()

    # Title style
    title_style = ParagraphStyle(
        "ReceiptTitle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#FF9933"),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )

    # Header style
    header_style = ParagraphStyle(
        "ReceiptHeader",
        parent=styles["Normal"],
        fontSize=14,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    # Temple header
    if temple:
        if temple_logo_path:
            try:
                logo = Image(temple_logo_path, width=1.2 * inch, height=1.2 * inch)
                logo.hAlign = "CENTER"
                elements.append(logo)
                elements.append(Spacer(1, 0.1 * inch))
            except:
                pass

        if temple.name:
            elements.append(Paragraph(temple.name, title_style))

        if temple.address:
            elements.append(Paragraph(temple.address, header_style))

        if temple.phone:
            elements.append(Paragraph(f"Phone: {temple.phone}", styles["Normal"]))

        if temple.email:
            elements.append(Paragraph(f"Email: {temple.email}", styles["Normal"]))

        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph("_" * 80, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    # Receipt title
    elements.append(Paragraph("SEVA BOOKING RECEIPT", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Receipt details table
    # Receipt Date / Booking Date = when the booking was made (created_at.date())
    # Seva Date = when the seva will be performed (booking_date)
    receipt_date = booking.created_at.date() if booking.created_at else None
    receipt_data = [
        ["Receipt Number:", booking.receipt_number or f"SEV{booking.id}"],
        ["Receipt Date:", receipt_date.strftime("%d-%m-%Y") if receipt_date else ""],
        ["Seva Date:", booking.booking_date.strftime("%d-%m-%Y") if booking.booking_date else ""],
        ["Seva Time:", booking.booking_time or "All Day"],
        ["Seva Name:", seva.name_english if seva else "N/A"],
        ["Devotee Name:", devotee.name if devotee else "N/A"],
        ["Phone:", devotee.phone if devotee else "N/A"],
        ["Address:", devotee.address if devotee and devotee.address else "N/A"],
        ["Payment Mode:", booking.payment_method.upper() if booking.payment_method else "Cash"],
        ["Amount Paid:", f"₹ {booking.amount_paid:,.2f}"],
    ]

    # Add additional booking details if available
    if booking.gotra:
        receipt_data.append(["Gotra:", booking.gotra])
    if booking.nakshatra:
        receipt_data.append(["Nakshatra:", booking.nakshatra])
    if booking.rashi:
        receipt_data.append(["Rashi:", booking.rashi])
    if booking.special_request:
        receipt_data.append(["Special Request:", booking.special_request])
    if booking.payment_method == "UPI" and booking.upi_reference_number:
        receipt_data.append(["UPI Reference:", booking.upi_reference_number])
    if booking.payment_method == "Cheque" and booking.cheque_number:
        receipt_data.append(["Cheque Number:", booking.cheque_number])
        if booking.cheque_bank_name:
            receipt_data.append(["Bank Name:", booking.cheque_bank_name])
    if booking.payment_method == "Online" and booking.utr_number:
        receipt_data.append(["UTR Number:", booking.utr_number])

    receipt_table = Table(receipt_data, colWidths=[2.5 * inch, 4 * inch])
    receipt_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )

    elements.append(receipt_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Amount in words
    amount_words = f"Rupees {_number_to_words(int(booking.amount_paid))} Only"
    elements.append(Paragraph(f"<b>Amount in Words:</b> {amount_words}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Booking status note
    status_note = ""
    if booking.status == SevaBookingStatus.PENDING:
        status_note = "This booking is pending approval."
    elif booking.status == SevaBookingStatus.CONFIRMED:
        status_note = "This booking is confirmed. Please arrive on time."
    elif booking.status == SevaBookingStatus.COMPLETED:
        status_note = "This seva has been completed."
    elif booking.status == SevaBookingStatus.CANCELLED:
        status_note = "This booking has been cancelled."

    if status_note:
        elements.append(Paragraph(f"<b>Status:</b> {status_note}", styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    # Footer
    footer_style = ParagraphStyle(
        "ReceiptFooter",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )

    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("_" * 80, styles["Normal"]))
    elements.append(Spacer(1, 0.1 * inch))

    if temple and temple.authorized_signatory_name:
        elements.append(
            Paragraph(f"Authorized Signatory: {temple.authorized_signatory_name}", styles["Normal"])
        )
        if temple.authorized_signatory_designation:
            elements.append(Paragraph(temple.authorized_signatory_designation, styles["Normal"]))

    elements.append(Spacer(1, 0.2 * inch))
    elements.append(
        Paragraph(f"Generated on {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", footer_style)
    )
    elements.append(Paragraph("MandirMitra Temple Management System", footer_style))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    return buffer


@router.get("/bookings/{booking_id}/receipt/pdf")
def get_seva_booking_receipt_pdf(
    booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Generate PDF receipt for a seva booking
    Professional receipt format with temple details
    """
    # Get booking with relationships loaded
    booking = (
        db.query(SevaBooking)
        .options(
            joinedload(SevaBooking.seva),
            joinedload(SevaBooking.devotee),
            joinedload(SevaBooking.user),
        )
        .filter(SevaBooking.id == booking_id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Generate PDF using helper function
    temple_id = current_user.temple_id if current_user else None
    buffer = _generate_seva_receipt_pdf(booking, db, temple_id)

    receipt_number = booking.receipt_number or f"SEV{booking.id}"
    filename = f"seva_receipt_{receipt_number}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/bookings/{booking_id}/receipt/pdf-base64")
def get_seva_booking_receipt_pdf_base64(
    booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Generate PDF receipt as base64 encoded string (for direct download without browser PDF handler)
    """
    import base64

    # Get booking with relationships loaded
    booking = (
        db.query(SevaBooking)
        .options(
            joinedload(SevaBooking.seva),
            joinedload(SevaBooking.devotee),
            joinedload(SevaBooking.user),
        )
        .filter(SevaBooking.id == booking_id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Generate PDF using the same logic
    temple_id = current_user.temple_id if current_user else None
    pdf_buffer = _generate_seva_receipt_pdf(booking, db, temple_id)

    # Convert to base64
    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode("utf-8")

    receipt_number = booking.receipt_number or f"SEV{booking.id}"
    return {
        "filename": f"seva_receipt_{receipt_number}.pdf",
        "content": pdf_base64,
        "receipt_number": receipt_number,
    }


@router.post("/bookings/transfer-advance-to-income")
def transfer_advance_booking_to_income(
    booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Transfers an advance seva booking amount from Advance Seva Booking (3003)
    to Seva Income (3002) on the actual seva date.
    This endpoint should be called on the seva date (can be automated via scheduled task).
    """
    if (
        current_user.role not in ["admin", "accountant", "temple_manager"]
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Only authorized users can perform this action")

    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Seva booking not found")

    if booking.booking_date > date.today():
        raise HTTPException(
            status_code=400, detail="Cannot transfer advance booking before the actual seva date"
        )

    temple_id = current_user.temple_id
    if not temple_id:
        # Try to get from booking
        if booking.devotee and hasattr(booking.devotee, "temple_id"):
            temple_id = booking.devotee.temple_id
        elif booking.user and hasattr(booking.user, "temple_id"):
            temple_id = booking.user.temple_id
        else:
            raise HTTPException(status_code=400, detail="User is not associated with a temple.")

    # Check if already transferred
    existing_transfer_entry = (
        db.query(JournalEntry)
        .filter(
            JournalEntry.reference_type == TransactionType.ADVANCE_SEVA_TRANSFER,
            JournalEntry.reference_id == booking.id,
        )
        .first()
    )

    if existing_transfer_entry:
        raise HTTPException(status_code=400, detail="Advance booking already transferred to income")

    # Get accounts
    advance_seva_account = (
        db.query(Account)
        .filter(
            Account.temple_id == temple_id, Account.account_code == "21003"  # Advance Seva Booking
        )
        .first()
    )

    seva_income_account = (
        db.query(Account)
        .filter(
            Account.temple_id == temple_id, Account.account_code == "42002"  # Seva Income - General
        )
        .first()
    )

    if not advance_seva_account:
        raise HTTPException(
            status_code=400,
            detail="Advance Seva Booking account (3003) not found. Please create it in Chart of Accounts.",
        )
    if not seva_income_account:
        raise HTTPException(
            status_code=400,
            detail="Seva Income account (3002) not found. Please create it in Chart of Accounts.",
        )

    # Create journal entry for transfer
    narration = (
        f"Transfer of advance seva booking {booking.receipt_number} to Seva Income on seva date"
    )
    # For transfer entries, entry_date should be booking_date (the seva date when transfer happens)
    entry_date = datetime.combine(booking.booking_date, datetime.min.time())

    # Generate entry number
    year = booking.booking_date.year
    prefix = f"JE/{year}/"
    last_entry = (
        db.query(JournalEntry)
        .filter(JournalEntry.temple_id == temple_id, JournalEntry.entry_number.like(f"{prefix}%"))
        .order_by(JournalEntry.id.desc())
        .first()
    )

    new_num = 1
    if last_entry and last_entry.entry_number:
        try:
            last_num = int(last_entry.entry_number.split("/")[-1])
            new_num = last_num + 1
        except ValueError:
            pass  # Fallback to 1 if parsing fails

    entry_number = f"{prefix}{new_num:04d}"

    journal_entry = JournalEntry(
        temple_id=temple_id,
        entry_date=entry_date,
        entry_number=entry_number,
        narration=narration,
        reference_type=TransactionType.ADVANCE_SEVA_TRANSFER,
        reference_id=booking.id,
        total_amount=booking.amount_paid,
        status=JournalEntryStatus.POSTED,
        created_by=current_user.id,
        posted_by=current_user.id,
        posted_at=datetime.utcnow(),
    )
    db.add(journal_entry)
    db.flush()

    # Debit: Advance Seva Booking (Liability decreases)
    debit_line = JournalLine(
        journal_entry_id=journal_entry.id,
        account_id=advance_seva_account.id,
        debit_amount=booking.amount_paid,
        credit_amount=0,
        description=f"Transfer from Advance Seva Booking for booking {booking.receipt_number}",
    )

    # Credit: Seva Income (Income increases)
    credit_line = JournalLine(
        journal_entry_id=journal_entry.id,
        account_id=seva_income_account.id,
        debit_amount=0,
        credit_amount=booking.amount_paid,
        description=f"Transfer to Seva Income for booking {booking.receipt_number}",
    )

    db.add(debit_line)
    db.add(credit_line)
    db.commit()

    return {
        "message": f"Advance booking {booking.receipt_number} transferred to Seva Income successfully."
    }


def _transfer_advance_bookings_batch_internal(db: Session, temple_id: int, created_by_user_id: int):
    """
    Internal function to transfer advance bookings to income.
    Can be called from endpoint or startup task.

    CRITICAL TIMING LOGIC:
    - Processes bookings with booking_date == (today - 1) i.e., YESTERDAY
    - Example: On Dec 23, 2025 morning, processes bookings with booking_date == Dec 22, 2025
    - On Dec 22, 2025 morning, processes bookings with booking_date == Dec 21, 2025

    WHY YESTERDAY, NOT TODAY?
    - Sevas are often performed in the evening, so on the seva date morning, status is still pending
    - We cannot transfer on the seva date morning because the seva hasn't happened yet
    - We must wait until the NEXT DAY (morning after seva date) to ensure seva is definitely complete
    - This prevents premature income recognition before seva is actually performed
    """
    from datetime import timedelta

    today = date.today()
    yesterday = today - timedelta(days=1)

    # Find all advance bookings where:
    # 1. booking_date == yesterday (seva date was YESTERDAY - seva definitely completed)
    #    Example: On Dec 23 morning, yesterday = Dec 22, so we process Dec 22 bookings
    #    This means seva on Dec 22 evening has been completed by Dec 23 morning
    # 2. Booking is not cancelled
    # 3. Has an accounting entry (to verify it's an advance booking credited to 21003)

    bookings_yesterday = (
        db.query(SevaBooking)
        .filter(
            SevaBooking.booking_date
            == yesterday,  # Only YESTERDAY's bookings (seva date has definitely passed)
            SevaBooking.status != SevaBookingStatus.CANCELLED,
        )
        .all()
    )

    transferred_count = 0
    errors = []
    skipped_count = 0

    for booking in bookings_yesterday:
        # Check if already transferred
        existing_transfer = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.reference_type == TransactionType.ADVANCE_SEVA_TRANSFER,
                JournalEntry.reference_id == booking.id,
            )
            .first()
        )

        if existing_transfer:
            skipped_count += 1
            continue  # Already transferred, skip

        # Verify this was an advance booking (credited to 3003)
        # Check if booking has an accounting entry that credits account 3003
        seva_entry = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.reference_type == TransactionType.SEVA,
                JournalEntry.reference_id == booking.id,
            )
            .first()
        )

        if not seva_entry:
            # No accounting entry - skip (shouldn't happen, but handle gracefully)
            skipped_count += 1
            continue

        # Check if the credit line is for account 3003 (Advance Seva Booking)
        credit_line = (
            db.query(JournalLine)
            .join(Account)
            .filter(
                JournalLine.journal_entry_id == seva_entry.id,
                JournalLine.credit_amount > 0,
                Account.account_code == "21003",
            )
            .first()
        )

        if not credit_line:
            # This was not an advance booking (likely same-day, credited to 3002) - skip
            skipped_count += 1
            continue

        # Get booking's temple_id
        booking_temple_id = temple_id
        if booking.devotee and hasattr(booking.devotee, "temple_id") and booking.devotee.temple_id:
            booking_temple_id = booking.devotee.temple_id
        elif booking.user and hasattr(booking.user, "temple_id") and booking.user.temple_id:
            booking_temple_id = booking.user.temple_id

        # Get accounts for this temple
        advance_seva_account = (
            db.query(Account)
            .filter(Account.temple_id == booking_temple_id, Account.account_code == "21003")
            .first()
        )

        seva_income_account = (
            db.query(Account)
            .filter(Account.temple_id == booking_temple_id, Account.account_code == "42002")
            .first()
        )

        if not advance_seva_account or not seva_income_account:
            errors.append(
                f"Booking {booking.receipt_number}: Accounts not found for temple {booking_temple_id}"
            )
            continue

        try:
            # Create transfer entry
            narration = f"Transfer of advance seva booking {booking.receipt_number} to Seva Income on seva date"
            # For transfer entries, entry_date should be booking_date (the seva date when transfer happens)
            entry_date = datetime.combine(booking.booking_date, datetime.min.time())

            year = booking.booking_date.year
            prefix = f"JE/{year}/"
            from sqlalchemy.orm import load_only

            last_entry = (
                db.query(JournalEntry)
                .options(
                    load_only(JournalEntry.id, JournalEntry.entry_number, JournalEntry.temple_id)
                )
                .filter(
                    JournalEntry.temple_id == booking_temple_id,
                    JournalEntry.entry_number.like(f"{prefix}%"),
                )
                .order_by(JournalEntry.id.desc())
                .first()
            )

            new_num = 1
            if last_entry and last_entry.entry_number:
                try:
                    last_num = int(last_entry.entry_number.split("/")[-1])
                    new_num = last_num + 1
                except ValueError:
                    pass

            entry_number = f"{prefix}{new_num:04d}"

            journal_entry = JournalEntry(
                temple_id=booking_temple_id,
                entry_date=entry_date,
                entry_number=entry_number,
                narration=narration,
                reference_type=TransactionType.ADVANCE_SEVA_TRANSFER,
                reference_id=booking.id,
                total_amount=booking.amount_paid,
                status=JournalEntryStatus.POSTED,
                created_by=created_by_user_id,
                posted_by=created_by_user_id,
                posted_at=datetime.utcnow(),
            )
            db.add(journal_entry)
            db.flush()

            debit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=advance_seva_account.id,
                debit_amount=booking.amount_paid,
                credit_amount=0,
                description=f"Transfer from Advance Seva Booking for booking {booking.receipt_number}",
            )

            credit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=seva_income_account.id,
                debit_amount=0,
                credit_amount=booking.amount_paid,
                description=f"Transfer to Seva Income for booking {booking.receipt_number}",
            )

            db.add(debit_line)
            db.add(credit_line)
            transferred_count += 1
        except Exception as e:
            errors.append(f"Booking {booking.receipt_number}: {str(e)}")
            db.rollback()
            continue

    return {
        "message": f"Transferred {transferred_count} advance booking(s) to Seva Income. Skipped {skipped_count} booking(s) (not advance bookings or already transferred).",
        "transferred_count": transferred_count,
        "skipped_count": skipped_count,
        "errors": errors if errors else None,
    }


@router.post("/bookings/transfer-advance-batch")
def transfer_advance_bookings_batch(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Batch transfer all advance bookings whose seva date was YESTERDAY (booking_date == today - 1).

    This should be called every morning when system initializes or via scheduled task/cron.

    CRITICAL TIMING LOGIC:
    - Processes bookings with booking_date == (today - 1) i.e., YESTERDAY
    - Example: On Dec 23, 2025 morning, processes bookings with booking_date == Dec 22, 2025
    - On Dec 22, 2025 morning, processes bookings with booking_date == Dec 21, 2025 (up to Dec 21)

    WHY YESTERDAY, NOT TODAY?
    - Sevas are often performed in the evening, so on the seva date morning, status is still pending
    - We cannot transfer on the seva date morning because the seva hasn't happened yet
    - We must wait until the NEXT DAY (morning after seva date) to ensure seva is definitely complete
    - This prevents premature income recognition before seva is actually performed

    Accounting Entry:
    - Dr: Advance Seva Booking (21003), Cr: Seva Income (42002)
    - Entry date: booking_date (the seva date when transfer happens)

    Returns count of bookings transferred.
    """
    if (
        current_user.role not in ["admin", "accountant", "temple_manager"]
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Only authorized users can perform this action")

    temple_id = current_user.temple_id
    if not temple_id:
        raise HTTPException(status_code=400, detail="User is not associated with a temple.")

    today = date.today()

    # Find all advance bookings where:
    # 1. booking_date == yesterday (seva date was YESTERDAY - seva definitely completed)
    # 2. Booking is not cancelled
    # 3. Has an accounting entry (to verify it's an advance booking credited to 3003)

    from datetime import timedelta

    yesterday = today - timedelta(days=1)

    bookings_yesterday = (
        db.query(SevaBooking)
        .filter(
            SevaBooking.booking_date
            == yesterday,  # Only YESTERDAY's bookings (seva date has passed)
            SevaBooking.status != SevaBookingStatus.CANCELLED,
        )
        .all()
    )

    transferred_count = 0
    errors = []
    skipped_count = 0

    for booking in bookings_yesterday:
        # Check if already transferred
        existing_transfer = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.reference_type == TransactionType.ADVANCE_SEVA_TRANSFER,
                JournalEntry.reference_id == booking.id,
            )
            .first()
        )

        if existing_transfer:
            skipped_count += 1
            continue  # Already transferred, skip

        # Verify this was an advance booking (credited to 3003)
        # Check if booking has an accounting entry that credits account 3003
        seva_entry = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.reference_type == TransactionType.SEVA,
                JournalEntry.reference_id == booking.id,
            )
            .first()
        )

        if not seva_entry:
            # No accounting entry - skip (shouldn't happen, but handle gracefully)
            skipped_count += 1
            continue

        # Check if the credit line is for account 3003 (Advance Seva Booking)
        credit_line = (
            db.query(JournalLine)
            .join(Account)
            .filter(
                JournalLine.journal_entry_id == seva_entry.id,
                JournalLine.credit_amount > 0,
                Account.account_code == "21003",
            )
            .first()
        )

        if not credit_line:
            # This was not an advance booking (likely same-day, credited to 3002) - skip
            skipped_count += 1
            continue

        # Get booking's temple_id
        booking_temple_id = temple_id
        if booking.devotee and hasattr(booking.devotee, "temple_id") and booking.devotee.temple_id:
            booking_temple_id = booking.devotee.temple_id
        elif booking.user and hasattr(booking.user, "temple_id") and booking.user.temple_id:
            booking_temple_id = booking.user.temple_id

        # Get accounts for this temple
        advance_seva_account = (
            db.query(Account)
            .filter(Account.temple_id == booking_temple_id, Account.account_code == "21003")
            .first()
        )

        seva_income_account = (
            db.query(Account)
            .filter(Account.temple_id == booking_temple_id, Account.account_code == "42002")
            .first()
        )

        if not advance_seva_account or not seva_income_account:
            errors.append(
                f"Booking {booking.receipt_number}: Accounts not found for temple {booking_temple_id}"
            )
            continue

        try:
            # Create transfer entry
            narration = f"Transfer of advance seva booking {booking.receipt_number} to Seva Income on seva date"
            # For transfer entries, entry_date should be booking_date (the seva date when transfer happens)
            entry_date = datetime.combine(booking.booking_date, datetime.min.time())

            year = booking.booking_date.year
            prefix = f"JE/{year}/"
            from sqlalchemy.orm import load_only

            last_entry = (
                db.query(JournalEntry)
                .options(
                    load_only(JournalEntry.id, JournalEntry.entry_number, JournalEntry.temple_id)
                )
                .filter(
                    JournalEntry.temple_id == booking_temple_id,
                    JournalEntry.entry_number.like(f"{prefix}%"),
                )
                .order_by(JournalEntry.id.desc())
                .first()
            )

            new_num = 1
            if last_entry and last_entry.entry_number:
                try:
                    last_num = int(last_entry.entry_number.split("/")[-1])
                    new_num = last_num + 1
                except ValueError:
                    pass

            entry_number = f"{prefix}{new_num:04d}"

            journal_entry = JournalEntry(
                temple_id=booking_temple_id,
                entry_date=entry_date,
                entry_number=entry_number,
                narration=narration,
                reference_type=TransactionType.ADVANCE_SEVA_TRANSFER,
                reference_id=booking.id,
                total_amount=booking.amount_paid,
                status=JournalEntryStatus.POSTED,
                created_by=current_user.id,
                posted_by=current_user.id,
                posted_at=datetime.utcnow(),
            )
            db.add(journal_entry)
            db.flush()

            debit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=advance_seva_account.id,
                debit_amount=booking.amount_paid,
                credit_amount=0,
                description=f"Transfer from Advance Seva Booking for booking {booking.receipt_number}",
            )

            credit_line = JournalLine(
                journal_entry_id=journal_entry.id,
                account_id=seva_income_account.id,
                debit_amount=0,
                credit_amount=booking.amount_paid,
                description=f"Transfer to Seva Income for booking {booking.receipt_number}",
            )

            db.add(debit_line)
            db.add(credit_line)
            transferred_count += 1
        except Exception as e:
            errors.append(f"Booking {booking.receipt_number}: {str(e)}")
            db.rollback()
            continue

    db.commit()

    return {
        "message": f"Transferred {transferred_count} advance booking(s) to Seva Income.",
        "transferred_count": transferred_count,
        "errors": errors if errors else None,
    }


@router.post("/bookings/{booking_id}/create-accounting")
def create_accounting_for_booking(
    booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Manually create accounting entry for an existing seva booking that doesn't have one.
    Useful if booking was created before account 3003 existed, etc.

    This will create the appropriate journal entry:
    - For advance bookings: Dr Cash/Bank, Cr 3003 (Advance Seva Booking)
    - For same-day bookings: Dr Cash/Bank, Cr 3002 (Seva Income)
    """
    if (
        current_user.role not in ["admin", "accountant", "temple_manager"]
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Only authorized users can perform this action")

    booking = db.query(SevaBooking).filter(SevaBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Seva booking not found")

    # Check if accounting entry already exists
    existing_entry = (
        db.query(JournalEntry)
        .filter(
            JournalEntry.reference_type == TransactionType.SEVA,
            JournalEntry.reference_id == booking.id,
        )
        .first()
    )

    if existing_entry:
        raise HTTPException(
            status_code=400,
            detail=f"Accounting entry already exists for this booking (Entry: {existing_entry.entry_number})",
        )

    temple_id = current_user.temple_id
    if not temple_id:
        # Try to get from booking
        if booking.devotee and hasattr(booking.devotee, "temple_id"):
            temple_id = booking.devotee.temple_id
        elif booking.user and hasattr(booking.user, "temple_id"):
            temple_id = booking.user.temple_id
        else:
            raise HTTPException(
                status_code=400, detail="Could not determine temple_id for this booking"
            )

    try:
        # Create accounting entry using the same function as new bookings
        journal_entry = post_seva_to_accounting(db, booking, temple_id)
        db.commit()

        return {
            "status": "success",
            "message": f"Accounting entry created for booking {booking.receipt_number}",
            "entry_number": journal_entry.entry_number,
            "entry_date": journal_entry.entry_date.isoformat(),
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create accounting entry: {str(e)}")
