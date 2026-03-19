"""
Safely correct donations posted to the wrong temple tenant.

Default mode is DRY RUN (no database writes).
Use --apply --yes to execute changes.

Examples:
  python -m scripts.fix_cross_temple_donations --source-temple-id 1 --target-temple-id 2
  python -m scripts.fix_cross_temple_donations --source-temple-id 1 --target-temple-id 2 --created-by-user-id 5 --from-date 2026-03-01 --apply --yes
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

from sqlalchemy.orm import Session, joinedload

# Add backend root to import app modules when run as a script
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.api.donations import post_donation_to_accounting
from app.core.coa_bootstrap import ensure_default_coa_for_temple
from app.core.database import SessionLocal
from app.models.accounting import Account, JournalEntry, TransactionType
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.seva import SevaBooking
from app.models.temple import Temple
import app.models as models_pkg


def preload_model_registry() -> None:
    '''
    Import all app.models modules so SQLAlchemy relationship strings resolve
    before mapper configuration is triggered by the first query.
    '''
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


def ensure_target_category(
    db: Session,
    source_category: Optional[DonationCategory],
    target_temple_id: int,
    *,
    apply_changes: bool,
) -> tuple[Optional[DonationCategory], bool]:
    if source_category is None:
        return None, False

    if source_category.temple_id in (None, target_temple_id):
        return source_category, False

    existing_target = (
        db.query(DonationCategory)
        .filter(
            DonationCategory.temple_id == target_temple_id,
            DonationCategory.name == source_category.name,
        )
        .first()
    )
    if existing_target:
        return existing_target, False

    if not apply_changes:
        return None, False

    target_account_id = map_account_to_target(db, source_category.account_id, target_temple_id)

    new_category = DonationCategory(
        temple_id=target_temple_id,
        name=source_category.name,
        description=source_category.description,
        is_80g_eligible=source_category.is_80g_eligible,
        is_active=source_category.is_active,
        display_order=source_category.display_order,
        account_id=target_account_id,
    )
    db.add(new_category)
    db.flush()
    return new_category, True


def collect_related_journal_entries(db: Session, donation_ids: Iterable[int]) -> dict[int, list[JournalEntry]]:
    ids = list(donation_ids)
    if not ids:
        return {}

    rows = (
        db.query(JournalEntry)
        .filter(
            JournalEntry.reference_type == TransactionType.DONATION,
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
    moving_donation_ids: set[int],
    *,
    apply_changes: bool,
) -> tuple[bool, str]:
    if devotee.temple_id == target_temple_id:
        return False, "already-target"

    if devotee.temple_id != source_temple_id:
        return False, "different-source"

    remaining_source_donations = (
        db.query(Donation.id)
        .filter(
            Donation.devotee_id == devotee.id,
            Donation.temple_id == source_temple_id,
            Donation.id.notin_(moving_donation_ids),
        )
        .count()
    )
    if remaining_source_donations > 0:
        return False, "still-used-by-source-donations"

    remaining_source_sevas = (
        db.query(SevaBooking.id)
        .filter(
            SevaBooking.devotee_id == devotee.id,
            SevaBooking.temple_id == source_temple_id,
        )
        .count()
    )
    if remaining_source_sevas > 0:
        return False, "still-used-by-source-sevas"

    if apply_changes:
        devotee.temple_id = target_temple_id
        devotee.updated_at = datetime.utcnow().isoformat()

    return True, "retagged"


def export_candidates_csv(path: str, donations: list[Donation], source: Temple, target: Temple) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(
            [
                "donation_id",
                "receipt_number",
                "amount",
                "donation_date",
                "created_by",
                "current_temple_id",
                "current_temple_name",
                "target_temple_id",
                "target_temple_name",
                "devotee_id",
                "devotee_name",
                "category_id",
                "category_name",
            ]
        )
        for donation in donations:
            writer.writerow(
                [
                    donation.id,
                    donation.receipt_number,
                    donation.amount,
                    donation.donation_date,
                    donation.created_by,
                    donation.temple_id,
                    source.name,
                    target.id,
                    target.name,
                    donation.devotee_id,
                    donation.devotee.name if donation.devotee else "",
                    donation.category_id,
                    donation.category.name if donation.category else "",
                ]
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Correct donations posted to the wrong temple tenant")
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
            db.query(Donation)
            .options(joinedload(Donation.devotee), joinedload(Donation.category))
            .filter(Donation.temple_id == source_temple.id)
        )

        if not args.include_cancelled:
            query = query.filter(Donation.is_cancelled == False)

        if args.created_by_user_id:
            query = query.filter(Donation.created_by == args.created_by_user_id)

        if from_date:
            query = query.filter(Donation.donation_date >= from_date)

        if to_date:
            query = query.filter(Donation.donation_date <= to_date)

        if args.receipt:
            query = query.filter(Donation.receipt_number.in_(args.receipt))

        if args.receipt_prefix:
            query = query.filter(Donation.receipt_number.like(f"{args.receipt_prefix}%"))

        query = query.order_by(Donation.donation_date.asc(), Donation.id.asc())
        if args.limit and args.limit > 0:
            query = query.limit(args.limit)

        donations = query.all()

        if not donations:
            print("[INFO] No matching donations found. Nothing to correct.")
            return 0

        total_amount = sum(float(d.amount or 0.0) for d in donations)
        print("=" * 80)
        print("Cross-Temple Donation Correction")
        print("=" * 80)
        print(f"Source Temple : {source_temple.id} - {source_temple.name}")
        print(f"Target Temple : {target_temple.id} - {target_temple.name}")
        print(f"Mode          : {'APPLY' if args.apply else 'DRY RUN'}")
        print(f"Rows          : {len(donations)}")
        print(f"Total Amount  : {total_amount:,.2f}")
        print("-" * 80)

        preview_limit = min(20, len(donations))
        for donation in donations[:preview_limit]:
            print(
                f"{donation.id:>6} | {donation.receipt_number:<22} | {donation.donation_date} | "
                f"{float(donation.amount or 0.0):>10.2f} | devotee={donation.devotee_id} | category={donation.category_id}"
            )
        if len(donations) > preview_limit:
            print(f"... ({len(donations) - preview_limit} more rows)")

        if args.export_csv:
            export_candidates_csv(args.export_csv, donations, source_temple, target_temple)
            print(f"[INFO] Exported candidate rows to {args.export_csv}")

        ensure_default_coa_for_temple(db, target_temple.id, raise_on_error=False)

        moving_donation_ids = {donation.id for donation in donations}
        related_entries = collect_related_journal_entries(db, moving_donation_ids)

        entry_ids_to_delete: set[int] = set()
        devotee_retagged = 0
        devotee_skipped = 0
        category_created = 0

        for donation in donations:
            target_category, was_category_created = ensure_target_category(
                db,
                donation.category,
                target_temple.id,
                apply_changes=args.apply,
            )

            if was_category_created:
                category_created += 1

            if donation.category and donation.category.temple_id not in (None, target_temple.id) and target_category and target_category.id != donation.category.id:
                donation.category_id = target_category.id
            elif donation.category and donation.category.temple_id not in (None, target_temple.id) and not target_category:
                print(
                    f"[WARN] Could not map category '{donation.category.name}' for donation {donation.receipt_number}; "
                    "it will use the source category id in dry run."
                )

            if donation.devotee is not None:
                changed, reason = retag_devotee_if_safe(
                    db,
                    donation.devotee,
                    source_temple.id,
                    target_temple.id,
                    moving_donation_ids,
                    apply_changes=args.apply,
                )
                if changed:
                    devotee_retagged += 1
                elif reason != "already-target":
                    devotee_skipped += 1

            donation.temple_id = target_temple.id
            donation.updated_at = datetime.utcnow().isoformat()

            if donation.journal_entry_id:
                entry_ids_to_delete.add(donation.journal_entry_id)
                if args.apply:
                    donation.journal_entry_id = None

            for entry in related_entries.get(donation.id, []):
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
        for donation in donations:
            new_entry = post_donation_to_accounting(db, donation, target_temple.id)
            if new_entry:
                donation.journal_entry_id = new_entry.id
                rebuilt_entries += 1

        db.commit()

        print("[SUCCESS] Correction applied.")
        print(f"[SUCCESS] Donations moved: {len(donations)}")
        print(f"[SUCCESS] Journal entries rebuilt: {rebuilt_entries}")
        print(f"[SUCCESS] Devotees retagged: {devotee_retagged}")
        print(f"[SUCCESS] Target categories created: {category_created}")
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


