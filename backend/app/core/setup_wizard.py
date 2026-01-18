"""
Setup Wizard - Creates temple record from configuration
"""

from sqlalchemy.orm import Session
from app.models.temple import Temple
from app.models.user import User
from app.core.security import get_password_hash
from app.core.interactive_setup import load_config
from pathlib import Path


def create_temple_from_config(db: Session, base_dir: Path):
    """Create temple record from configuration file"""
    config = load_config(base_dir)
    if not config:
        return None
    
    # Check if temple already exists
    existing_temple = db.query(Temple).filter(Temple.name == config['temple_name']).first()
    if existing_temple:
        return existing_temple
    
    # Create slug from temple name (make it URL-safe and unique)
    base_slug = config['db_name'].lower().replace(' ', '-').replace('_', '-')
    slug = base_slug
    counter = 1
    # Ensure slug is unique
    while db.query(Temple).filter(Temple.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Create new temple
    temple = Temple(
        name=config['temple_name'],
        address=config.get('address', ''),
        city=config.get('city', ''),
        state=config.get('state', ''),
        pincode=config.get('pincode'),
        phone=config.get('phone'),
        email=config.get('email'),
        primary_deity=config.get('primary_deity'),
        slug=slug,
    )
    
    db.add(temple)
    db.flush()  # Get temple ID
    
    # Create admin user
    admin_email = config.get('admin_email', 'admin@temple.com')
    existing_user = db.query(User).filter(User.email == admin_email).first()
    
    if not existing_user:
        admin_user = User(
            email=admin_email,
            password_hash=get_password_hash(config.get('admin_password', 'admin123')),
            full_name="Admin User",
            role="temple_manager",
            is_active=True,
            temple_id=temple.id
        )
        db.add(admin_user)
    
    db.commit()
    return temple

