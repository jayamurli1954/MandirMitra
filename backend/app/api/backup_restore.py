"""
Database Backup and Restore API Endpoints
Allows administrators to backup and restore the database
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse, JSONResponse
from datetime import datetime
import os
import json
from pathlib import Path
from typing import Optional

from app.core.database import get_db, engine
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/backup-restore", tags=["backup-restore"])


@router.get("/status")
def get_backup_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get backup status and information"""
    # Check if user is admin
    if current_user.role not in ['admin', 'super_admin', 'temple_manager']:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access backup/restore features"
        )
    
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Get list of backup files
    backup_files = []
    if backup_dir.exists():
        for file_path in sorted(backup_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            stat = file_path.stat()
            backup_files.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size_mb": round(stat.st_size / (1024 * 1024), 2)
            })
    
    return {
        "backup_directory": str(backup_dir.absolute()),
        "backup_files": backup_files[:10],  # Latest 10 backups
        "total_backups": len(backup_files)
    }


@router.post("/backup")
def create_backup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a backup of critical database tables"""
    # Check if user is admin
    if current_user.role not in ['admin', 'super_admin', 'temple_manager']:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create backups"
        )
    
    try:
        from sqlalchemy import text, inspect
        
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.json"
        
        # Tables to backup (excluding system tables)
        tables_to_backup = [
            'temples', 'users', 'devotees', 'donation_categories', 'donations',
            'sevas', 'seva_bookings', 'accounts', 'journal_entries', 'journal_lines',
            'bank_accounts', 'donation_categories'
        ]
        
        backup_data = {
            "backup_timestamp": datetime.now().isoformat(),
            "backed_up_by": current_user.email,
            "tables": {}
        }
        
        # Backup each table
        for table_name in tables_to_backup:
            try:
                # Check if table exists
                inspector = inspect(engine)
                if table_name not in inspector.get_table_names():
                    continue
                
                # Get all rows from table
                result = db.execute(text(f"SELECT * FROM {table_name}"))
                rows = []
                columns = list(result.keys())
                
                for row in result:
                    row_dict = {}
                    # Handle both Row objects and tuples
                    if hasattr(row, '_mapping'):
                        # SQLAlchemy Row object
                        for col in columns:
                            value = row[col]
                            # Convert datetime/date to string
                            if hasattr(value, 'isoformat'):
                                row_dict[col] = value.isoformat()
                            else:
                                row_dict[col] = value
                    else:
                        # Tuple row
                        for i, col in enumerate(columns):
                            value = row[i]
                            if hasattr(value, 'isoformat'):
                                row_dict[col] = value.isoformat()
                            else:
                                row_dict[col] = value
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
    # Check if user is admin
    if current_user.role not in ['admin', 'super_admin', 'temple_manager']:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can download backups"
        )
    
    backup_dir = Path("backups")
    backup_file = backup_dir / filename
    
    # Security: Only allow JSON files from backup directory
    if not filename.endswith('.json') or not backup_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Backup file not found"
        )
    
    # Ensure file is in backup directory (prevent path traversal)
    try:
        backup_file.resolve().relative_to(backup_dir.resolve())
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Invalid backup file path"
        )
    
    return FileResponse(
        path=str(backup_file),
        filename=filename,
        media_type='application/json'
    )


@router.delete("/delete/{filename}")
def delete_backup(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a backup file"""
    # Check if user is admin
    if current_user.role not in ['admin', 'super_admin', 'temple_manager']:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can delete backups"
        )
    
    backup_dir = Path("backups")
    backup_file = backup_dir / filename
    
    # Security checks
    if not filename.endswith('.json') or not backup_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Backup file not found"
        )
    
    try:
        backup_file.resolve().relative_to(backup_dir.resolve())
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Invalid backup file path"
        )
    
    try:
        backup_file.unlink()
        return {
            "status": "success",
            "message": f"Backup file {filename} deleted successfully"
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
    # Check if user is admin
    if current_user.role not in ['admin', 'super_admin']:
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
        from sqlalchemy import text
        
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
        for table_name, table_data in backup_data["tables"].items():
            try:
                # Delete existing data (optional - you might want to merge instead)
                # db.execute(text(f"DELETE FROM {table_name}"))
                
                # Insert restored data
                if table_data["rows"]:
                    columns = table_data["columns"]
                    rows = table_data["rows"]
                    
                    # Build INSERT statement (using ON CONFLICT for PostgreSQL, or simple INSERT for others)
                    columns_str = ", ".join(columns)
                    placeholders = ", ".join([f":{col}" for col in columns])
                    
                    # Check database type
                    db_url = str(engine.url)
                    if 'postgresql' in db_url.lower():
                        insert_stmt = text(f"""
                            INSERT INTO {table_name} ({columns_str})
                            VALUES ({placeholders})
                            ON CONFLICT DO NOTHING
                        """)
                    else:
                        # For SQLite, use INSERT OR IGNORE
                        insert_stmt = text(f"""
                            INSERT OR IGNORE INTO {table_name} ({columns_str})
                            VALUES ({placeholders})
                        """)
                    
                    for row in rows:
                        db.execute(insert_stmt, row)
                    
                    restored_tables.append(table_name)
                    restored_records += len(rows)
                
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

