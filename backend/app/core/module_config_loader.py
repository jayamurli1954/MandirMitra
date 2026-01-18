"""
Module Configuration Loader
Automatically applies module configuration from file on startup
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.models.temple import Temple
from app.core.database import SessionLocal


def load_module_config_file() -> Optional[Dict]:
    """Load module configuration from JSON file"""
    # Look for module_config.json in project root (parent of backend)
    config_file = Path(__file__).parent.parent.parent / "module_config.json"
    
    if not config_file.exists():
        # Try in backend directory
        config_file = Path(__file__).parent.parent / "module_config.json"
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config
        except Exception as e:
            print(f"⚠️  Could not load module config file: {e}")
    
    return None


def apply_module_config_to_temples():
    """Apply module configuration to all temples"""
    config = load_module_config_file()
    if not config:
        return
    
    db: Session = SessionLocal()
    try:
        temples = db.query(Temple).all()
        for temple in temples:
            updated = False
            for key, value in config.items():
                if hasattr(temple, key):
                    current_value = getattr(temple, key)
                    if current_value != value:
                        setattr(temple, key, value)
                        updated = True
            
            if updated:
                db.commit()
                print(f"✅ Applied module configuration to temple: {temple.name}")
    except Exception as e:
        print(f"⚠️  Could not apply module configuration: {e}")
        db.rollback()
    finally:
        db.close()

















