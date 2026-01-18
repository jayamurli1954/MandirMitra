"""
Auto-Setup for Standalone Packages
Automatically configures SQLite database for non-technical users
"""

import os
import sys
from pathlib import Path
from app.core.config import settings
from app.core.interactive_setup import get_database_path, load_config, setup_complete


def get_standalone_database_path() -> Path:
    """Get the path for SQLite database in standalone mode"""
    # Try multiple methods to find the base directory
    base_dir = None
    
    # Method 1: Check for STANDALONE_BASE_DIR environment variable (set by launcher)
    if os.environ.get("STANDALONE_BASE_DIR"):
        base_dir = Path(os.environ["STANDALONE_BASE_DIR"])
    
    # Method 2: Check if running as compiled executable
    elif getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    
    # Method 3: Look for module_config.json in parent directories (standalone package marker)
    else:
        current = Path(__file__).resolve()
        # Look up to 4 levels up for module_config.json
        for i in range(4):
            check_dir = current.parents[i] if i < len(current.parents) else None
            if check_dir and (check_dir / "module_config.json").exists():
                base_dir = check_dir
                break
        
        # Fallback: assume standard structure (3 levels up from this file)
        if base_dir is None:
            base_dir = Path(__file__).parent.parent.parent
    
    # Ensure base_dir is absolute
    base_dir = base_dir.resolve()
    
    # Load temple configuration to get temple name
    config = load_config(base_dir)
    temple_name = config.get('db_name') if config else None
    
    # Get database path based on temple name
    db_path = get_database_path(base_dir, temple_name)
    return db_path


def setup_standalone_database():
    """Setup SQLite database for standalone mode"""
    db_path = get_standalone_database_path()
    db_url = f"sqlite:///{db_path.absolute()}"
    
    # Set environment variable to override config
    os.environ["DATABASE_URL"] = db_url
    
    # Load config to show temple name (reuse path detection from get_standalone_database_path)
    base_dir = db_path.parent.parent  # db_path is in data/ subdirectory
    config = load_config(base_dir)
    if config:
        temple_name = config.get('temple_name', 'Unknown')
        print(f"[INFO] Using SQLite database for: {temple_name}")
        print(f"[INFO] Database file: {db_path.name}")
    else:
        print(f"[INFO] Using SQLite database: {db_path.name}")
    
    return db_url


def is_standalone_mode() -> bool:
    """Check if running in standalone mode (for non-technical users)"""
    # Check if DATABASE_URL environment variable is explicitly set to SQLite
    if os.environ.get("DATABASE_URL", "").startswith("sqlite"):
        return True
    
    # Check DEPLOYMENT_MODE setting (defaults to standalone)
    if settings.DEPLOYMENT_MODE.lower() == "standalone":
        return True
    
    # Check if DATABASE_URL is set to default PostgreSQL (user hasn't configured it)
    default_postgres = "postgresql://postgres:password@localhost:5432/temple_db"
    current_db_url = os.environ.get("DATABASE_URL")
    if current_db_url is None:
        # Not set in environment, check settings
        current_db_url = settings.DATABASE_URL
        if current_db_url == default_postgres:
            # Using default, so standalone mode
            return True
    
    # Also check if we're in a standalone package (has module_config.json)
    # Check current directory and parent directories
    current = Path(__file__).resolve()
    for i in range(4):
        check_dir = current.parents[i] if i < len(current.parents) else None
        if check_dir and (check_dir / "module_config.json").exists():
            return True
    
    return False

