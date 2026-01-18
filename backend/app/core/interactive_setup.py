"""
Interactive Setup Wizard for Standalone Installation
Asks for temple information and creates configuration
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional


def sanitize_filename(name: str) -> str:
    """Convert temple name to safe filename"""
    # Remove invalid characters for Windows filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    # Remove leading/trailing spaces and dots
    name = name.strip(' .')
    # Limit length
    if len(name) > 50:
        name = name[:50]
    return name or "temple"


def run_interactive_setup(base_dir: Path) -> Dict:
    """
    Run interactive setup wizard to collect temple information
    Returns configuration dictionary
    """
    print("=" * 70)
    print("  MandirMitra - Temple Management System")
    print("  Initial Setup Wizard")
    print("=" * 70)
    print()
    print("Welcome! Let's set up your temple information.")
    print("Please provide the following details:")
    print()
    
    config = {}
    
    # Temple Name (Mandatory)
    while True:
        temple_name = input("1. Temple Name (Required): ").strip()
        if temple_name:
            config['temple_name'] = temple_name
            config['db_name'] = sanitize_filename(temple_name)
            break
        print("   [ERROR] Temple name is required. Please enter a name.")
    
    print()
    
    # Address (Mandatory)
    while True:
        address = input("2. Temple Address (Required): ").strip()
        if address:
            config['address'] = address
            break
        print("   [ERROR] Address is required. Please enter an address.")
    
    print()
    
    # City (Mandatory)
    while True:
        city = input("3. City (Required): ").strip()
        if city:
            config['city'] = city
            break
        print("   [ERROR] City is required. Please enter a city name.")
    
    print()
    
    # State (Mandatory)
    while True:
        state = input("4. State (Required): ").strip()
        if state:
            config['state'] = state
            break
        print("   [ERROR] State is required. Please enter a state name.")
    
    print()
    
    # Pincode (Optional but recommended)
    pincode = input("5. Pincode (Optional): ").strip()
    if pincode:
        config['pincode'] = pincode
    
    print()
    
    # Phone (Optional)
    phone = input("6. Phone Number (Optional): ").strip()
    if phone:
        config['phone'] = phone
    
    print()
    
    # Email (Optional)
    email = input("7. Email Address (Optional): ").strip()
    if email:
        config['email'] = email
    
    print()
    
    # Primary Deity (Optional)
    deity = input("8. Primary Deity (Optional, e.g., 'Lord Shiva'): ").strip()
    if deity:
        config['primary_deity'] = deity
    
    print()
    
    # Admin User Details
    print("Admin User Setup:")
    print("-" * 70)
    
    admin_email = input("9. Admin Email (default: admin@temple.com): ").strip()
    config['admin_email'] = admin_email if admin_email else "admin@temple.com"
    
    admin_password = input("10. Admin Password (default: admin123): ").strip()
    config['admin_password'] = admin_password if admin_password else "admin123"
    
    print()
    print("=" * 70)
    print("  Setup Summary")
    print("=" * 70)
    print(f"Temple Name: {config['temple_name']}")
    print(f"Database Name: {config['db_name']}.db")
    print(f"Address: {config['address']}")
    print(f"City: {config['city']}")
    print(f"State: {config['state']}")
    if config.get('pincode'):
        print(f"Pincode: {config['pincode']}")
    if config.get('phone'):
        print(f"Phone: {config['phone']}")
    if config.get('email'):
        print(f"Email: {config['email']}")
    if config.get('primary_deity'):
        print(f"Primary Deity: {config['primary_deity']}")
    print(f"Admin Email: {config['admin_email']}")
    print()
    
    confirm = input("Is this information correct? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Setup cancelled. Please run the setup again.")
        return None
    
    return config


def save_config(config: Dict, base_dir: Path):
    """Save configuration to file"""
    config_file = base_dir / "temple_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    print(f"\n[OK] Configuration saved to: {config_file}")


def load_config(base_dir: Path) -> Optional[Dict]:
    """Load existing configuration"""
    config_file = base_dir / "temple_config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load config: {e}")
    return None


def get_database_path(base_dir: Path, temple_name: Optional[str] = None) -> Path:
    """Get database path based on temple name"""
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    if temple_name:
        db_name = sanitize_filename(temple_name)
        return data_dir / f"{db_name}.db"
    else:
        # Fallback to default
        return data_dir / "temple.db"


def setup_complete(base_dir: Path) -> bool:
    """Check if setup has been completed"""
    config_file = base_dir / "temple_config.json"
    return config_file.exists()

















