"""
Seva API Endpoints
Handles temple sevas/poojas/archanas
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, MetaData, Table, select
from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel
import io

from app.core.database import get_db, column_exists
from app.core.security import get_current_user
from app.core.coa_bootstrap import ensure_default_coa_for_temple
from app.core.auto_setup import is_standalone_mode
from app.models.user import User
from app.models.seva import Seva, SevaBooking, SevaCategory, SevaAvailability, SevaBookingStatus
from app.models.devotee import Devotee
from app.models.temple import Temple
from app.models.accounting import (
    Account,
    AccountSubType,
    JournalEntry,
    JournalLine,
    JournalEntryStatus,
    TransactionType,
)
from app.models.upi_banking import BankAccount
from app.schemas.seva import (
    SevaCreate,
    SevaUpdate,
    SevaResponse,
    SevaListResponse,
    SevaBookingCreate,
    SevaBookingUpdate,
    SevaBookingResponse,
)
from app.services.printer.print_queue import get_print_queue
from app.services.notification_service import notification_service
from app.constants.hindu_constants import GOTHRAS, NAKSHATRAS, RASHIS
from app.services.seva_accounting_service import (
    get_payment_accounts_for_temple as _svc_get_payment_accounts_for_temple,
    post_seva_to_accounting,
)
from app.services.seva_receipt_service import generate_seva_receipt_pdf
from app.services.seva_booking_flow_service import (
    list_bookings as _svc_list_bookings,
    get_booking as _svc_get_booking,
    create_booking as _svc_create_booking,
    update_booking as _svc_update_booking,
    cancel_booking as _svc_cancel_booking,
)
from app.services.seva_reschedule_service import (
    validate_reschedule_target_date as _svc_validate_reschedule_target_date,
    request_reschedule as _svc_request_reschedule,
    get_pending_reschedule_requests as _svc_get_pending_reschedule_requests,
    approve_reschedule as _svc_approve_reschedule,
)
from app.services.seva_refund_service import (
    process_refund as _svc_process_refund,
    get_refund_status as _svc_get_refund_status,
)
from app.services.seva_transfer_service import (
    transfer_advance_booking_to_income as _svc_transfer_advance_booking_to_income,
    transfer_advance_bookings_batch_internal as _svc_transfer_advance_bookings_batch_internal,
    transfer_advance_bookings_batch as _svc_transfer_advance_bookings_batch,
    create_accounting_for_booking as _svc_create_accounting_for_booking,
)

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


def _get_payment_accounts_for_temple(db: Session, temple_id: Optional[int]) -> dict:
    return _svc_get_payment_accounts_for_temple(db, temple_id)


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


@router.get("/payment-accounts")
def get_payment_accounts_for_sevas(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get active cash and bank accounts for seva booking payment selection."""
    temple_id = current_user.temple_id if current_user else None
    return _get_payment_accounts_for_temple(db, temple_id)


@router.get("/{seva_id}", response_model=SevaResponse)
def get_seva(seva_id: int, db: Session = Depends(get_db)):
    """Get seva details"""
    seva = get_seva_safely(db, seva_id=seva_id)
    if not seva:
        raise HTTPException(status_code=404, detail="Seva not found")
    return seva


@router.post("/", response_model=SevaResponse, status_code=201)
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
            ip_address=request.client.host if request and request.client else None,
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
                    import ast
                    parsed = ast.literal_eval(update_data["except_days"])
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
            ip_address=request.client.host if request and request.client else None,
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
    from app.core.audit import get_entity_dict
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
            ip_address=request.client.host if request and request.client else None,
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
    bookings = _svc_list_bookings(
        db=db,
        current_user=current_user,
        seva_id=seva_id,
        devotee_id=devotee_id,
        booking_date=booking_date,
        status=status,
        skip=skip,
        limit=limit,
    )
    return [SevaBookingResponse(**serialize_booking_response(booking)) for booking in bookings]

@router.get("/bookings/{booking_id}", response_model=SevaBookingResponse)
def get_booking(
    booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get booking details"""
    return _svc_get_booking(db=db, booking_id=booking_id, current_user=current_user)

@router.post("/bookings/", response_model=SevaBookingResponse, status_code=201)
def create_booking(
    booking_data: SevaBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new seva booking"""
    booking = _svc_create_booking(
        db=db,
        booking_data=booking_data,
        current_user=current_user,
        get_seva_safely_fn=get_seva_safely,
        post_seva_to_accounting_fn=post_seva_to_accounting,
    )
    return SevaBookingResponse(**serialize_booking_response(booking))

@router.put("/bookings/{booking_id}", response_model=SevaBookingResponse)
def update_booking(
    booking_id: int,
    booking_data: SevaBookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update booking"""
    return _svc_update_booking(
        db=db,
        booking_id=booking_id,
        booking_data=booking_data,
        current_user=current_user,
    )

@router.delete("/bookings/{booking_id}")
def cancel_booking(
    booking_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel booking"""
    return _svc_cancel_booking(
        db=db,
        booking_id=booking_id,
        reason=reason,
        current_user=current_user,
    )

# ===== SEVA RESCHEDULE (POSTPONE/PREPONE) =====


def _validate_reschedule_target_date(
    db: Session,
    booking: SevaBooking,
    new_date: date,
    check_advance_limit: bool = True,
):
    return _svc_validate_reschedule_target_date(
        db=db,
        booking=booking,
        new_date=new_date,
        check_advance_limit=check_advance_limit,
    )

@router.put("/bookings/{booking_id}/reschedule")
def request_reschedule(
    booking_id: int,
    new_date: date = Query(..., description="New booking date"),
    reason: str = Query(..., description="Reason for reschedule"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Request to reschedule (postpone/prepone) a seva booking"""
    return _svc_request_reschedule(
        db=db,
        booking_id=booking_id,
        new_date=new_date,
        reason=reason,
        current_user=current_user,
    )

@router.get("/reschedule/pending", response_model=List[SevaBookingResponse])
@router.get("/bookings/pending-reschedule", response_model=List[SevaBookingResponse])  # backward compatibility
def get_pending_reschedule_requests(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get all pending reschedule requests (admin/temple_manager only)"""
    bookings = _svc_get_pending_reschedule_requests(db=db, current_user=current_user)
    return [SevaBookingResponse(**serialize_booking_response(booking)) for booking in bookings]

@router.post("/bookings/{booking_id}/approve-reschedule")
def approve_reschedule(
    booking_id: int,
    approve: bool = Query(..., description="Approve (true) or reject (false)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve or reject a reschedule request (admin only)"""
    return _svc_approve_reschedule(
        db=db,
        booking_id=booking_id,
        approve=approve,
        current_user=current_user,
    )

# ===== PRIEST ASSIGNMENT =====


@router.get("/lists/priests")
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
    """Process refund for a cancelled booking"""
    return _svc_process_refund(
        db=db,
        booking_id=booking_id,
        current_user=current_user,
        refund_amount=refund_amount,
        refund_method=refund_method,
        refund_reference=refund_reference,
    )

@router.get("/bookings/{booking_id}/refund-status", response_model=dict)
def get_refund_status(
    booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get refund status for a cancelled booking"""
    return _svc_get_refund_status(db=db, booking_id=booking_id)

def _generate_seva_receipt_pdf(booking: SevaBooking, db: Session, temple_id: int = None):
    return generate_seva_receipt_pdf(booking, db, temple_id)

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
    """Transfers an advance seva booking amount from Advance Seva Booking to Seva Income."""
    return _svc_transfer_advance_booking_to_income(
        db=db,
        booking_id=booking_id,
        current_user=current_user,
    )

def _transfer_advance_bookings_batch_internal(db: Session, temple_id: int, created_by_user_id: int):
    return _svc_transfer_advance_bookings_batch_internal(
        db=db,
        temple_id=temple_id,
        created_by_user_id=created_by_user_id,
    )

@router.post("/bookings/transfer-advance-batch")
def transfer_advance_bookings_batch(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Batch transfer all advance bookings whose seva date was yesterday."""
    return _svc_transfer_advance_bookings_batch(
        db=db,
        current_user=current_user,
    )

@router.post("/bookings/{booking_id}/create-accounting")
def create_accounting_for_booking(
    booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Manually create accounting entry for an existing seva booking."""
    return _svc_create_accounting_for_booking(
        db=db,
        booking_id=booking_id,
        current_user=current_user,
        post_seva_to_accounting_fn=post_seva_to_accounting,
    )
