"""
Panchang Display Settings Model
Stores temple-specific preferences for panchang display
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class PanchangDisplaySettings(Base):
    """Temple-specific panchang display configuration"""
    
    __tablename__ = "panchang_display_settings"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Temple (one-to-one relationship)
    temple_id = Column(Integer, ForeignKey("temples.id"), unique=True, nullable=False, index=True)
    
    # ========== ELEMENT VISIBILITY SETTINGS ==========
    # Essential Elements (Priority 1)
    show_tithi = Column(Boolean, default=True)
    show_nakshatra = Column(Boolean, default=True)
    show_yoga = Column(Boolean, default=True)
    show_karana = Column(Boolean, default=True)
    show_vara = Column(Boolean, default=True)
    show_sun_timings = Column(Boolean, default=True)
    show_rahu_kaal = Column(Boolean, default=True)
    
    # Secondary Elements (Priority 2)
    show_yamaganda = Column(Boolean, default=True)
    show_gulika = Column(Boolean, default=True)
    show_abhijit_muhurat = Column(Boolean, default=True)
    show_brahma_muhurat = Column(Boolean, default=True)
    show_festivals = Column(Boolean, default=True)
    show_fasting_info = Column(Boolean, default=True)
    
    # Advanced Elements (Priority 3)
    show_choghadiya = Column(Boolean, default=False)
    show_hora = Column(Boolean, default=False)
    show_planetary_positions = Column(Boolean, default=False)
    show_panchak_warning = Column(Boolean, default=True)
    show_recommendations = Column(Boolean, default=True)
    show_moon_timings = Column(Boolean, default=False)
    
    # ========== DISPLAY FORMAT SETTINGS ==========
    # Language
    primary_language = Column(String(20), default="en")  # en, hi, sa, ta, te, kn, mr, bn, gu
    secondary_language = Column(String(20), default="hi")  # For bilingual display
    show_sanskrit_names = Column(Boolean, default=True)
    
    # Time Format
    time_format_12h = Column(Boolean, default=True)  # True = 12h (AM/PM), False = 24h
    show_timezone = Column(Boolean, default=False)
    
    # Date Format
    show_gregorian_date = Column(Boolean, default=True)
    show_hindu_date = Column(Boolean, default=True)
    show_samvat = Column(Boolean, default=True)  # Vikram/Shaka Samvat
    
    # ========== VISUAL SETTINGS ==========
    # Color Scheme
    auspicious_color = Column(String(7), default="#28A745")  # Green
    inauspicious_color = Column(String(7), default="#DC3545")  # Red
    neutral_color = Column(String(7), default="#007BFF")  # Blue
    special_color = Column(String(7), default="#FF9933")  # Saffron
    
    # Icons
    show_icons = Column(Boolean, default=True)
    show_quality_stars = Column(Boolean, default=True)  # ⭐⭐⭐ for nakshatra quality
    
    # ========== CONTENT SETTINGS ==========
    # Detailed Information
    show_tithi_end_time = Column(Boolean, default=True)
    show_nakshatra_pada = Column(Boolean, default=True)
    show_nakshatra_deity = Column(Boolean, default=True)
    show_nakshatra_quality = Column(Boolean, default=True)
    show_karana_half = Column(Boolean, default=True)  # First/Second half
    
    # Warnings
    highlight_inauspicious = Column(Boolean, default=True)
    show_avoid_activities = Column(Boolean, default=True)  # What to avoid during Rahu Kaal, etc.
    show_best_for_activities = Column(Boolean, default=True)  # What's good for today
    
    # ========== LAYOUT SETTINGS ==========
    # Display Mode
    display_mode = Column(String(20), default="compact")  # compact, detailed, full
    show_on_dashboard = Column(Boolean, default=True)
    show_on_public_website = Column(Boolean, default=True)
    
    # Widget Settings
    widget_size = Column(String(20), default="medium")  # small, medium, large
    show_expandable_sections = Column(Boolean, default=True)
    
    # ========== ADDITIONAL SETTINGS ==========
    # Update Frequency
    auto_refresh_enabled = Column(Boolean, default=True)
    refresh_interval_minutes = Column(Integer, default=60)  # Check for transitions
    
    # Print Settings
    print_format = Column(String(20), default="a4")  # a4, compact, detailed
    include_temple_header = Column(Boolean, default=True)
    include_verification_note = Column(Boolean, default=True)
    
    # Custom Settings (JSON for flexibility)
    custom_settings = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    temple = relationship("Temple", back_populates="panchang_display_settings")
    
    def __repr__(self):
        return f"<PanchangDisplaySettings(temple_id={self.temple_id}, display_mode='{self.display_mode}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "temple_id": self.temple_id,
            "show_tithi": self.show_tithi,
            "show_nakshatra": self.show_nakshatra,
            "show_yoga": self.show_yoga,
            "show_karana": self.show_karana,
            "show_vara": self.show_vara,
            "show_sun_timings": self.show_sun_timings,
            "show_rahu_kaal": self.show_rahu_kaal,
            "show_yamaganda": self.show_yamaganda,
            "show_gulika": self.show_gulika,
            "show_abhijit_muhurat": self.show_abhijit_muhurat,
            "show_brahma_muhurat": self.show_brahma_muhurat,
            "show_festivals": self.show_festivals,
            "show_fasting_info": self.show_fasting_info,
            "show_choghadiya": self.show_choghadiya,
            "show_hora": self.show_hora,
            "show_planetary_positions": self.show_planetary_positions,
            "show_panchak_warning": self.show_panchak_warning,
            "show_recommendations": self.show_recommendations,
            "show_moon_timings": self.show_moon_timings,
            "primary_language": self.primary_language,
            "secondary_language": self.secondary_language,
            "show_sanskrit_names": self.show_sanskrit_names,
            "time_format_12h": self.time_format_12h,
            "show_timezone": self.show_timezone,
            "show_gregorian_date": self.show_gregorian_date,
            "show_hindu_date": self.show_hindu_date,
            "show_samvat": self.show_samvat,
            "auspicious_color": self.auspicious_color,
            "inauspicious_color": self.inauspicious_color,
            "neutral_color": self.neutral_color,
            "special_color": self.special_color,
            "show_icons": self.show_icons,
            "show_quality_stars": self.show_quality_stars,
            "show_tithi_end_time": self.show_tithi_end_time,
            "show_nakshatra_pada": self.show_nakshatra_pada,
            "show_nakshatra_deity": self.show_nakshatra_deity,
            "show_nakshatra_quality": self.show_nakshatra_quality,
            "show_karana_half": self.show_karana_half,
            "highlight_inauspicious": self.highlight_inauspicious,
            "show_avoid_activities": self.show_avoid_activities,
            "show_best_for_activities": self.show_best_for_activities,
            "display_mode": self.display_mode,
            "show_on_dashboard": self.show_on_dashboard,
            "show_on_public_website": self.show_on_public_website,
            "widget_size": self.widget_size,
            "show_expandable_sections": self.show_expandable_sections,
            "auto_refresh_enabled": self.auto_refresh_enabled,
            "refresh_interval_minutes": self.refresh_interval_minutes,
            "print_format": self.print_format,
            "include_temple_header": self.include_temple_header,
            "include_verification_note": self.include_verification_note,
            "custom_settings": self.custom_settings or {},
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

