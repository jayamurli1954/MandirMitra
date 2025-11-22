"""
Panchang Display Settings Service
Business logic for managing panchang display settings
"""

from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.panchang_display_settings import PanchangDisplaySettings
from app.schemas.panchang_display_settings import (
    PanchangDisplaySettingsCreate,
    PanchangDisplaySettingsUpdate,
    PanchangDisplaySettingsPreset,
    PRESETS
)


class PanchangDisplaySettingsService:
    """Service for managing panchang display settings"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_temple_id(self, temple_id: int) -> Optional[PanchangDisplaySettings]:
        """Get panchang display settings for a temple"""
        return self.db.query(PanchangDisplaySettings).filter(
            PanchangDisplaySettings.temple_id == temple_id
        ).first()
    
    def get_or_create_default(self, temple_id: int) -> PanchangDisplaySettings:
        """Get existing settings or create default settings for a temple"""
        settings = self.get_by_temple_id(temple_id)
        
        if not settings:
            # Create default settings
            default_settings = PanchangDisplaySettings(
                temple_id=temple_id
            )
            self.db.add(default_settings)
            self.db.commit()
            self.db.refresh(default_settings)
            return default_settings
        
        return settings
    
    def create(self, settings_data: PanchangDisplaySettingsCreate) -> PanchangDisplaySettings:
        """Create new panchang display settings"""
        # Check if settings already exist for this temple
        existing = self.get_by_temple_id(settings_data.temple_id)
        if existing:
            raise ValueError(f"Panchang display settings already exist for temple_id {settings_data.temple_id}")
        
        # Create new settings
        settings_dict = settings_data.dict(exclude={'temple_id'})
        settings = PanchangDisplaySettings(
            temple_id=settings_data.temple_id,
            **settings_dict
        )
        
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        return settings
    
    def update(
        self,
        temple_id: int,
        settings_data: PanchangDisplaySettingsUpdate
    ) -> PanchangDisplaySettings:
        """Update panchang display settings for a temple"""
        settings = self.get_by_temple_id(temple_id)
        
        if not settings:
            raise ValueError(f"Panchang display settings not found for temple_id {temple_id}")
        
        # Update only provided fields
        update_data = settings_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)
        
        settings.updated_at = datetime.utcnow().isoformat()
        
        self.db.commit()
        self.db.refresh(settings)
        return settings
    
    def apply_preset(
        self,
        temple_id: int,
        preset_name: str
    ) -> PanchangDisplaySettings:
        """Apply a preset configuration to temple settings"""
        if preset_name not in PRESETS:
            available = ", ".join(PRESETS.keys())
            raise ValueError(f"Preset '{preset_name}' not found. Available: {available}")
        
        preset = PRESETS[preset_name]
        preset_settings = preset.settings.dict()
        
        # Get or create settings
        settings = self.get_or_create_default(temple_id)
        
        # Apply preset values
        for field, value in preset_settings.items():
            if hasattr(settings, field):
                setattr(settings, field, value)
        
        settings.updated_at = datetime.utcnow().isoformat()
        
        self.db.commit()
        self.db.refresh(settings)
        return settings
    
    def reset_to_defaults(self, temple_id: int) -> PanchangDisplaySettings:
        """Reset settings to default values"""
        settings = self.get_by_temple_id(temple_id)
        
        if not settings:
            return self.get_or_create_default(temple_id)
        
        # Reset all fields to defaults
        default_settings = PanchangDisplaySettings(temple_id=temple_id)
        
        for column in PanchangDisplaySettings.__table__.columns:
            if column.name not in ['id', 'temple_id', 'created_at', 'updated_at']:
                setattr(settings, column.name, getattr(default_settings, column.name))
        
        settings.updated_at = datetime.utcnow().isoformat()
        
        self.db.commit()
        self.db.refresh(settings)
        return settings
    
    def delete(self, temple_id: int) -> bool:
        """Delete panchang display settings for a temple"""
        settings = self.get_by_temple_id(temple_id)
        
        if not settings:
            return False
        
        self.db.delete(settings)
        self.db.commit()
        return True
    
    def get_available_presets(self) -> dict:
        """Get list of available presets"""
        return {
            name: {
                "name": preset.name,
                "description": preset.description
            }
            for name, preset in PRESETS.items()
        }

