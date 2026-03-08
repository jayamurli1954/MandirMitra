import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import MetaData, Table, inspect, select

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.models.temple import Temple

BACKUP_DIR = Path(settings.BACKUP_PATH).expanduser()
ALLOWED_TABLES = {
    "temples",
    "users",
    "devotees",
    "donation_categories",
    "donations",
    "sevas",
    "seva_bookings",
    "accounts",
    "journal_entries",
    "journal_lines",
    "bank_accounts",
}
AUTO_BACKUP_MARKER = "_auto_"
_backup_scheduler_thread: threading.Thread | None = None
_backup_scheduler_stop_event = threading.Event()


def _ensure_backup_dir() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def _collect_backup_data(temple_scope: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        backup_data: Dict[str, Any] = {
            "backup_timestamp": datetime.now().isoformat(),
            "backed_up_by": "system",
            "backup_kind": "auto",
            "temple_scope": temple_scope,
            "tables": {},
        }

        inspector = inspect(engine)
        metadata = MetaData()
        for table_name in ALLOWED_TABLES:
            if table_name not in inspector.get_table_names():
                continue
            try:
                table = Table(table_name, metadata, autoload_with=engine)
                stmt = select(table)
                if "temple_id" in table.c:
                    stmt = stmt.where(table.c.temple_id == temple_scope)
                result = db.execute(stmt).mappings().all()
                columns = [column.name for column in table.columns]
                rows: List[Dict[str, Any]] = []
                for row in result:
                    row_dict: Dict[str, Any] = {}
                    for col in columns:
                        value = row.get(col)
                        row_dict[col] = value.isoformat() if hasattr(value, "isoformat") else value
                    rows.append(row_dict)
                backup_data["tables"][table_name] = {
                    "columns": columns,
                    "rows": rows,
                    "count": len(rows),
                }
            except Exception as exc:
                print(f"Warning: Could not backup table {table_name}: {exc}")
        return backup_data
    finally:
        db.close()


def _cleanup_old_auto_backups(prefix: str) -> None:
    keep_count = max(1, settings.BACKUP_AUTO_KEEP_COUNT)
    files = sorted(
        [
            file_path
            for file_path in BACKUP_DIR.glob(f"{prefix}*.json")
            if AUTO_BACKUP_MARKER in file_path.name
        ],
        key=lambda file_path: file_path.stat().st_mtime,
        reverse=True,
    )
    for old_file in files[keep_count:]:
        try:
            old_file.unlink()
        except OSError as exc:
            print(f"Warning: Could not delete old auto backup {old_file}: {exc}")


def create_auto_backup_for_temple(temple_id: int) -> str:
    _ensure_backup_dir()
    prefix = f"backup_temple_{temple_id}_auto_"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"{prefix}{timestamp}.json"
    backup_data = _collect_backup_data(temple_id)
    with open(backup_file, "w", encoding="utf-8") as handle:
        json.dump(backup_data, handle, indent=2, ensure_ascii=False, default=str)
    _cleanup_old_auto_backups(prefix)
    return backup_file.name


def _run_backup_cycle() -> None:
    db = SessionLocal()
    try:
        temple_ids = [temple_id for (temple_id,) in db.query(Temple.id).filter(Temple.is_active == True).all()]
    finally:
        db.close()

    for temple_id in temple_ids:
        try:
            create_auto_backup_for_temple(temple_id)
        except Exception as exc:
            print(f"Warning: Automatic backup failed for temple_id={temple_id}: {exc}")


def _backup_scheduler_worker() -> None:
    interval_seconds = max(1, settings.BACKUP_AUTO_INTERVAL_MINUTES) * 60
    while not _backup_scheduler_stop_event.is_set():
        try:
            _run_backup_cycle()
        except Exception as exc:
            print(f"Warning: Automatic backup worker error: {exc}")
        _backup_scheduler_stop_event.wait(interval_seconds)


def start_backup_scheduler() -> None:
    global _backup_scheduler_thread
    if not settings.BACKUP_ENABLED or not settings.BACKUP_AUTO_ENABLED or settings.BACKUP_AUTO_INTERVAL_MINUTES <= 0:
        return
    if _backup_scheduler_thread and _backup_scheduler_thread.is_alive():
        return
    _backup_scheduler_stop_event.clear()
    _backup_scheduler_thread = threading.Thread(
        target=_backup_scheduler_worker,
        name="mandirmitra-backup-scheduler",
        daemon=True,
    )
    _backup_scheduler_thread.start()


def stop_backup_scheduler() -> None:
    global _backup_scheduler_thread
    _backup_scheduler_stop_event.set()
    if _backup_scheduler_thread and _backup_scheduler_thread.is_alive():
        _backup_scheduler_thread.join(timeout=2)
    _backup_scheduler_thread = None
