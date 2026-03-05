"""
Database Backup and Restore API Endpoints
Allows administrators to backup and restore the database
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse, JSONResponse
from datetime import datetime
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import re

from app.core.database import get_db, engine
from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/backup-restore", tags=["backup-restore"])

BACKUP_DIR = Path(settings.BACKUP_PATH).expanduser()
BACKUP_ALLOWED_ROLES = {"admin", "super_admin"}
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
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _require_backup_access(current_user: User) -> None:
    if current_user.role not in BACKUP_ALLOWED_ROLES and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access backup/restore features",
        )


def _is_super_admin(current_user: User) -> bool:
    return current_user.role == "super_admin" or bool(current_user.is_superuser)


def _backup_filename_prefix(current_user: User) -> str:
    if _is_super_admin(current_user):
        return "backup_global_"
    temple_id = current_user.temple_id
    if not temple_id:
        raise HTTPException(status_code=400, detail="Admin user must be associated with a temple")
    return f"backup_temple_{temple_id}_"


def _can_access_backup_file(current_user: User, filename: str) -> bool:
    if _is_super_admin(current_user):
        return True
    return filename.startswith(_backup_filename_prefix(current_user))


def _validate_identifier(identifier: str) -> bool:
    return bool(identifier and IDENTIFIER_RE.match(identifier))


def _safe_filename(filename: str) -> str:
    base = Path(filename).name
    if base != filename or not base.endswith(".json"):
        raise HTTPException(status_code=400, detail="Invalid backup file name")
    return base


def _ensure_backup_dir() -> None:
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    except (PermissionError, FileNotFoundError, OSError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Backup directory is not writable: {exc}",
        ) from exc


@router.get("/status")
def get_backup_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get backup status and information"""
    _require_backup_access(current_user)
    
    # Get list of backup files
    backup_files = []
    if BACKUP_DIR.exists():
        for file_path in sorted(BACKUP_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            if not _can_access_backup_file(current_user, file_path.name):
                continue
            stat = file_path.stat()
            backup_files.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size_mb": round(stat.st_size / (1024 * 1024), 2)
            })
    
    return {
        "backup_directory": str(BACKUP_DIR.absolute()),
        "backup_files": backup_files[:10],  # Latest 10 backups
        "total_backups": len(backup_files)
    }


@router.post("/backup")
def create_backup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a backup of critical database tables"""
    _require_backup_access(current_user)
    _ensure_backup_dir()
    
    try:
        from sqlalchemy import inspect, MetaData, Table, select
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"{_backup_filename_prefix(current_user)}{timestamp}.json"
        
        backup_data = {
            "backup_timestamp": datetime.now().isoformat(),
            "backed_up_by": current_user.email,
            "temple_scope": current_user.temple_id,
            "tables": {}
        }
        
        # Backup each table
        inspector = inspect(engine)
        metadata = MetaData()
        for table_name in ALLOWED_TABLES:
            try:
                # Check if table exists
                if table_name not in inspector.get_table_names():
                    continue
                table = Table(table_name, metadata, autoload_with=engine)
                stmt = select(table)
                if not _is_super_admin(current_user) and "temple_id" in table.c:
                    stmt = stmt.where(table.c.temple_id == current_user.temple_id)

                result = db.execute(stmt).mappings().all()
                columns = [c.name for c in table.columns]
                rows: List[Dict[str, Any]] = []
                for row in result:
                    row_dict: Dict[str, Any] = {}
                    for col in columns:
                        value = row.get(col)
                        row_dict[col] = value.isoformat() if hasattr(value, "isoformat") else value
                    rows.append(row_dict)
                
                backup_data["tables"][table_name] = {
                    "columns": list(columns),
                    "rows": rows,
                    "count": len(rows)
                }
                
            except Exception as e:
                # Skip tables that don't exist or can't be accessed
                print(f"Warning: Could not backup table {table_name}: {e}")
                continue
        
        # Save backup file
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
        
        file_size = backup_file.stat().st_size
        
        return {
            "status": "success",
            "message": "Backup created successfully",
            "backup_file": backup_file.name,
            "file_size": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "tables_backed_up": list(backup_data["tables"].keys()),
            "total_records": sum(t["count"] for t in backup_data["tables"].values()),
            "created_at": backup_data["backup_timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create backup: {str(e)}"
        )


@router.get("/download/{filename}")
def download_backup(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Download a backup file"""
    _require_backup_access(current_user)
    
    safe_name = _safe_filename(filename)
    if not _can_access_backup_file(current_user, safe_name):
        raise HTTPException(status_code=403, detail="Not authorized to access this backup file")
    backup_file = BACKUP_DIR / safe_name
    
    # Security: Only allow JSON files from backup directory
    if not backup_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Backup file not found"
        )
    
    # Ensure file is in backup directory (prevent path traversal)
    try:
        backup_file.resolve().relative_to(BACKUP_DIR.resolve())
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Invalid backup file path"
        )
    
    return FileResponse(
        path=str(backup_file),
        filename=safe_name,
        media_type='application/json'
    )


@router.delete("/delete/{filename}")
def delete_backup(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a backup file"""
    _require_backup_access(current_user)

    safe_name = _safe_filename(filename)
    if not _can_access_backup_file(current_user, safe_name):
        raise HTTPException(status_code=403, detail="Not authorized to delete this backup file")
    backup_file = BACKUP_DIR / safe_name
    
    # Security checks
    if not backup_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Backup file not found"
        )
    
    try:
        backup_file.resolve().relative_to(BACKUP_DIR.resolve())
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Invalid backup file path"
        )
    
    try:
        backup_file.unlink()
        return {
            "status": "success",
            "message": f"Backup file {safe_name} deleted successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete backup: {str(e)}"
        )


@router.post("/restore")
def restore_backup(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Restore database from backup file
    
    WARNING: This will overwrite existing data. Use with extreme caution!
    """
    # Restore is super-admin only
    if not _is_super_admin(current_user):
        raise HTTPException(
            status_code=403,
            detail="Only super administrators can restore backups"
        )
    
    # Only allow JSON files
    if not file.filename.endswith('.json'):
        raise HTTPException(
            status_code=400,
            detail="Only JSON backup files are supported"
        )
    
    try:
        from sqlalchemy import MetaData, Table, insert, inspect
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        
        # Read backup file
        content = file.file.read()
        backup_data = json.loads(content.decode('utf-8'))
        
        if "tables" not in backup_data:
            raise HTTPException(
                status_code=400,
                detail="Invalid backup file format"
            )
        
        restored_tables = []
        restored_records = 0
        
        # Restore each table
        inspector = inspect(engine)
        metadata = MetaData()
        for table_name, table_data in backup_data["tables"].items():
            try:
                if table_name not in ALLOWED_TABLES or not _validate_identifier(table_name):
                    continue
                if table_name not in inspector.get_table_names():
                    continue

                rows = table_data.get("rows", [])
                if not rows:
                    continue

                table = Table(table_name, metadata, autoload_with=engine)
                valid_columns = {c.name for c in table.columns}
                allowed_columns = [
                    c for c in table_data.get("columns", [])
                    if c in valid_columns and _validate_identifier(c)
                ]
                if not allowed_columns:
                    continue

                sanitized_rows = []
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    sanitized_row = {c: row.get(c) for c in allowed_columns if c in row}
                    if sanitized_row:
                        sanitized_rows.append(sanitized_row)

                if not sanitized_rows:
                    continue

                if engine.dialect.name == "postgresql":
                    stmt = pg_insert(table).on_conflict_do_nothing()
                elif engine.dialect.name == "sqlite":
                    stmt = insert(table).prefix_with("OR IGNORE")
                else:
                    stmt = insert(table)

                db.execute(stmt, sanitized_rows)
                restored_tables.append(table_name)
                restored_records += len(sanitized_rows)
                
            except Exception as e:
                print(f"Warning: Could not restore table {table_name}: {e}")
                continue
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Backup restored successfully",
            "restored_tables": restored_tables,
            "restored_records": restored_records,
            "restored_at": datetime.now().isoformat(),
            "restored_by": current_user.email
        }
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON file format"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restore backup: {str(e)}"
        )

