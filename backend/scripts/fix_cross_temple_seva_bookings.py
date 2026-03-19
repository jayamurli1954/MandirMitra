"""
Safely correct seva bookings posted to the wrong temple tenant.

Default mode is DRY RUN (no database writes).
Use --apply --yes to execute changes.

Examples:
  python -m scripts.fix_cross_temple_seva_bookings --source-temple-id 1 --target-temple-id 2
  python -m scripts.fix_cross_temple_seva_bookings --source-temple-id 1 --target-temple-id 2 --from-date 2026-03-01 --apply --yes
"""

from __future__ import annotations

import argparse
import csv
import importlib
import pkgutil
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

# Add backend root to import app modules when run as a script
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.coa_bootstrap import ensure_default_coa_for_temple
from app.core.database import SessionLocal
from app.models.accounting import Account, JournalEntry, TransactionType
from app.models.devotee import Devotee
from app.models.donation import Donation
from app.models.seva import Seva, SevaBooking, SevaBookingStatus
from app.models.temple import Temple
from app.services.seva_accounting_service import post_seva_to_accounting
import app.models as models_pkg


def preload_model_registry() -> None:
    """
    Import all app.models modules so SQLAlchemy relationship strings resolve
    before mapper configuration is triggered by the first query.
    """
    for _, module_name, _ in pkgutil.iter_modules(models_pkg.__path__):
        if module_name.startswith("__"):
            continue
        importlib.import_module(f"app.models.{module_name}")


def parse_date(raw: Optional[str]) -> Optional[date]:
    if not raw:
        return None
    return datetime.strptime(raw, "%Y-%m-%d").date()


def resolve_temple(db: Session, temple_id: Optional[int], temple_name: Optional[str]) -> Temple:
    if temple_id:
        temple = db.query(Temple).filter(Temple.id == temple_id).first()
        if not temple:
            raise ValueError(f"Temple with id={temple_id} was not found")
        return temple

    if temple_name:
        like_pattern = f"%{temple_name.strip()}%"
        temple = (
            db.query(Temple)
            .filter(
                (Temple.name.ilike(like_pattern))
                | (Temple.trust_name.ilike(like_pattern))
                | (Temple.slug.ilike(like_pattern))
            )
            .first()
        )
        if not temple:
            raise ValueError(f"Temple with name/trust/slug '{temple_name}' was not found")
        return temple

    raise ValueError("Provide either --source-temple-id/--target-temple-id or name variants")


def map_account_to_target(db: Session, source_account_id: Optional[int], target_temple_id: int) -> Optional[int]:
    if not source_account_id:
        return None

    source_account = db.query(Account).filter(Account.id == source_account_id).first()
    if not source_account:
        return None

    target_account = (
        db.query(Account)
        .filter(
            Account.temple_id == target_temple_id,
            Account.account_code == source_account.account_code,
        )
        .first()
    )
    return target_account.id if target_account else None


def ensure_target_seva(
    db: Session,
    source_seva: Optional[Seva],
    target_temple_id: int,
    *,
    apply_changes: bool,
) -> tuple[Optional[Seva], bool]:
    if source_seva is None:
        return None, False

    if source_seva.temple_id in (None, target_temple_id):
        return source_seva, False

    existing_target = (
        db.query(Seva)
        .filter(
            Seva.temple_id == target_temple_id,
            func.lower(Seva.name_english) == source_seva.name_english.lower(),
        )
        .first()
    )
    if existing_target:
        return existing_target, False

    if not apply_changes:
        return None, False

    mapped_account_id = map_account_to_target(db, source_seva.account_id, target_temple_id)

    new_seva = Seva(
        temple_id=target_temple_id,
        name_english=source_seva.name_english,
        name_kannada=source_seva.name_kannada,
        name_sanskrit=source_seva.name_sanskrit,
        description=source_seva.description,
        category=source_seva.category,
        amount=source_seva.amount,
        min_amount=source_seva.min_amount,
        max_amount=source_seva.max_amount,
        availability=source_seva.availability,
        specific_day=source_seva.specific_day,
        except_day=source_seva.except_day,
        except_days=source_seva.except_days,
        time_slot=source_seva.time_slot,
        max_bookings_per_day=source_seva.max_bookings_per_day,
        advance_booking_days=source_seva.advance_booking_days,
        requires_approval=source_seva.requires_approval,
        is_active=source_seva.is_active,
        is_token_seva=source_seva.is_token_seva,
        token_color=source_seva.token_color,
        token_threshold=source_seva.token_threshold,
        account_id=mapped_account_id,
        benefits=source_seva.benefits,
        instructions=source_seva.instructions,
        duration_minutes=source_seva.duration_minutes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_seva)
    db.flush()
    return new_seva, True


def collect_related_journal_entries(db: Session, booking_ids: Iterable[int]) -> dict[int, list[JournalEntry]]:
    ids = list(booking_ids)
    if not ids:
        return {}

    rows = (
        db.query(JournalEntry)
        .filter(
            JournalEntry.reference_type == TransactionType.SEVA,
            JournalEntry.reference_id.in_(ids),
        )
        .all()
    )

    grouped: dict[int, list[JournalEntry]] = defaultdict(list)
    for row in rows:
        if row.reference_id is not None:
            grouped[int(row.reference_id)].append(row)
    return grouped


def retag_devotee_if_safe(
    db: Session,
    devotee: Devotee,
    source_temple_id: int,
    target_temple_id: int,
    moving_booking_ids: set[int],
    *,
    apply_changes: bool,
) -> tuple[bool, str]:
    if devotee.temple_id == target_temple_id:
        return False, "already-target"

    if devotee.temple_id != source_temple_id:
        return False, "different-source"

    remaining_source_bookings = (
        db.query(SevaBooking.id)
        .filter(
            SevaBooking.devotee_id == devotee.id,
            SevaBooking.temple_id == source_temple_id,
            SevaBooking.id.notin_(moving_booking_ids),
        )
        .count()
    )
    if remaining_source_bookings > 0:
        return False, "still-used-by-source-bookings"

    remaining_source_donations = (
        db.query(Donation.id)
        .filter(
            Donation.devotee_id == devotee.id,
            Donation.temple_id == source_temple_id,
        )
        .count()
    )
    if remaining_source_donations > 0:
        return False, "still-used-by-source-donations"

    if apply_changes:
        devotee.temple_id = target_temple_id
        devotee.updated_at = datetime.utcnow().isoformat()

    return True, "retagged"


def export_candidates_csv(path: str, bookings: list[SevaBooking], source: Temple, target: Temple) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(
            [
                "booking_id",
                "receipt_number",
                "booking_date",
                "status",
                "amount_paid",
                "created_by_user_id",
                "current_temple_id",
                "current_temple_name",
                "target_temple_id",
                "target_temple_name",
                "seva_id",
                "seva_name",
                "devotee_id",
                "devotee_name",
            ]
        )
        for booking in bookings:
            writer.writerow(
                [
                    booking.id,
                    booking.receipt_number,
                    booking.booking_date,
                    booking.status.value if booking.status else "",
                    booking.amount_paid,
                    booking.user_id,
                    booking.temple_id,
                    source.name,
                    target.id,
                    target.name,
                    booking.seva_id,
                    booking.seva.name_english if booking.seva else "",
                    booking.devotee_id,
                    booking.devotee.name if booking.devotee else "",
                ]
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Correct seva bookings posted to the wrong temple tenant")
    parser.add_argument("--source-temple-id", type=int)
    parser.add_argument("--source-temple-name")
    parser.add_argument("--target-temple-id", type=int)
    parser.add_argument("--target-temple-name")
    parser.add_argument("--created-by-user-id", type=int, help="Optional filter by creator user id")
    parser.add_argument("--from-date", help="YYYY-MM-DD")
    parser.add_argument("--to-date", help="YYYY-MM-DD")
    parser.add_argument("--receipt", action="append", default=[], help="Specific receipt number(s) to move")
    parser.add_argument("--receipt-prefix", help="Filter receipts by prefix")
    parser.add_argument("--limit", type=int, default=0, help="Optional max rows to process")
    parser.add_argument("--include-cancelled", action="store_true")
    parser.add_argument("--export-csv", help="Optional file path to export candidate rows")
    parser.add_argument("--apply", action="store_true", help="Persist changes")
    parser.add_argument("--yes", action="store_true", help="Required with --apply")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    preload_model_registry()

    if args.apply and not args.yes:
        print("[ERROR] --apply requires --yes for safety")
        return 2

    db = SessionLocal()
    try:
        source_temple = resolve_temple(db, args.source_temple_id, args.source_temple_name)
        target_temple = resolve_temple(db, args.target_temple_id, args.target_temple_name)

        if source_temple.id == target_temple.id:
            raise ValueError("Source and target temples are the same")

        from_date = parse_date(args.from_date)
        to_date = parse_date(args.to_date)

        query = (
            db.query(SevaBooking)
            .options(joinedload(SevaBooking.seva), joinedload(SevaBooking.devotee))
            .filter(SevaBooking.temple_id == source_temple.id)
        )

        if not args.include_cancelled:
            query = query.filter(SevaBooking.status != SevaBookingStatus.CANCELLED)

        if args.created_by_user_id:
            query = query.filter(SevaBooking.user_id == args.created_by_user_id)

        if from_date:
            query = query.filter(SevaBooking.booking_date >= from_date)

        if to_date:
            query = query.filter(SevaBooking.booking_date <= to_date)

        if args.receipt:
            query = query.filter(SevaBooking.receipt_number.in_(args.receipt))

        if args.receipt_prefix:
            query = query.filter(SevaBooking.receipt_number.like(f"{args.receipt_prefix}%"))

        query = query.order_by(SevaBooking.booking_date.asc(), SevaBooking.id.asc())
        if args.limit and args.limit > 0:
            query = query.limit(args.limit)

        bookings = query.all()

        if not bookings:
            print("[INFO] No matching seva bookings found. Nothing to correct.")
            return 0

        total_amount = sum(float(b.amount_paid or 0.0) for b in bookings)
        print("=" * 80)
        print("Cross-Temple Seva Booking Correction")
        print("=" * 80)
        print(f"Source Temple : {source_temple.id} - {source_temple.name}")
        print(f"Target Temple : {target_temple.id} - {target_temple.name}")
        print(f"Mode          : {'APPLY' if args.apply else 'DRY RUN'}")
        print(f"Rows          : {len(bookings)}")
        print(f"Total Amount  : {total_amount:,.2f}")
        print("-" * 80)

        preview_limit = min(20, len(bookings))
        for booking in bookings[:preview_limit]:
            seva_name = booking.seva.name_english if booking.seva else ""
            print(
                f"{booking.id:>6} | {str(booking.receipt_number or ''):<22} | {booking.booking_date} | "
                f"{float(booking.amount_paid or 0.0):>10.2f} | seva={seva_name} | devotee={booking.devotee_id}"
            )
        if len(bookings) > preview_limit:
            print(f"... ({len(bookings) - preview_limit} more rows)")

        if args.export_csv:
            export_candidates_csv(args.export_csv, bookings, source_temple, target_temple)
            print(f"[INFO] Exported candidate rows to {args.export_csv}")

        ensure_default_coa_for_temple(db, target_temple.id, raise_on_error=False)

        moving_booking_ids = {booking.id for booking in bookings}
        related_entries = collect_related_journal_entries(db, moving_booking_ids)

        entry_ids_to_delete: set[int] = set()
        devotee_retagged = 0
        devotee_skipped = 0
        seva_created = 0

        for booking in bookings:
            target_seva, was_seva_created = ensure_target_seva(
                db,
                booking.seva,
                target_temple.id,
                apply_changes=args.apply,
            )

            if was_seva_created:
                seva_created += 1

            if booking.seva and booking.seva.temple_id not in (None, target_temple.id):
                if target_seva and target_seva.id != booking.seva_id:
                    booking.seva_id = target_seva.id
                elif not target_seva:
                    print(
                        f"[WARN] Could not map seva '{booking.seva.name_english}' for booking {booking.receipt_number}; "
                        "it will keep source seva id in dry run."
                    )

            if booking.devotee is not None:
                changed, reason = retag_devotee_if_safe(
                    db,
                    booking.devotee,
                    source_temple.id,
                    target_temple.id,
                    moving_booking_ids,
                    apply_changes=args.apply,
                )
                if changed:
                    devotee_retagged += 1
                elif reason != "already-target":
                    devotee_skipped += 1

            booking.temple_id = target_temple.id
            booking.updated_at = datetime.utcnow()

            for entry in related_entries.get(booking.id, []):
                entry_ids_to_delete.add(entry.id)

        print(f"[INFO] Related journal entries to rebuild: {len(entry_ids_to_delete)}")
        print(f"[INFO] Devotee retag candidates updated: {devotee_retagged}, skipped: {devotee_skipped}")

        if not args.apply:
            db.rollback()
            print("[DRY RUN] No changes were written.")
            return 0

        if entry_ids_to_delete:
            entries = db.query(JournalEntry).filter(JournalEntry.id.in_(entry_ids_to_delete)).all()
            for entry in entries:
                db.delete(entry)
            db.flush()

        rebuilt_entries = 0
        for booking in bookings:
            new_entry = post_seva_to_accounting(db, booking, target_temple.id)
            if new_entry:
                rebuilt_entries += 1

        db.commit()

        print("[SUCCESS] Correction applied.")
        print(f"[SUCCESS] Seva bookings moved: {len(bookings)}")
        print(f"[SUCCESS] Journal entries rebuilt: {rebuilt_entries}")
        print(f"[SUCCESS] Devotees retagged: {devotee_retagged}")
        print(f"[SUCCESS] Target sevas created: {seva_created}")
        return 0

    except Exception as exc:
        db.rollback()
        print(f"[ERROR] {exc}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
