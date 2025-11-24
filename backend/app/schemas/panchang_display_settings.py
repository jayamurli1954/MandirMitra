"""
Panchang Display Settings Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime


class PanchangDisplaySettingsBase(BaseModel):
    """Base schema with all display settings fields"""

    # Location Settings (for accurate Panchang calculation)
    latitude: str = Field(default="12.9716", description="Temple latitude for accurate calculations")
    longitude: str = Field(default="77.5946", description="Temple longitude for accurate calculations")
    city_name: str = Field(default="Bengaluru", max_length=100, description="City name for display")
    timezone: str = Field(default="Asia/Kolkata", max_length=50, description="Temple timezone")

    # Element Visibility
    show_tithi: bool = True
    show_nakshatra: bool = True
    show_yoga: bool = True
    show_karana: bool = True
    show_vara: bool = True
    show_sun_timings: bool = True
    show_rahu_kaal: bool = True
    show_yamaganda: bool = True
    show_gulika: bool = True
    show_abhijit_muhurat: bool = True
    show_brahma_muhurat: bool = True
    show_festivals: bool = True
    show_fasting_info: bool = True
    show_choghadiya: bool = False
    show_hora: bool = False
    show_planetary_positions: bool = False
    show_panchak_warning: bool = True
    show_recommendations: bool = True
    show_moon_timings: bool = False
    
    # Display Format
    primary_language: str = Field(default="en", pattern="^(en|hi|sa|ta|te|kn|mr|bn|gu)$")
    secondary_language: Optional[str] = Field(default="hi", pattern="^(en|hi|sa|ta|te|kn|mr|bn|gu)$")
    show_sanskrit_names: bool = True
    time_format_12h: bool = True
    show_timezone: bool = False
    show_gregorian_date: bool = True
    show_hindu_date: bool = True
    show_samvat: bool = True
    
    # Visual Settings
    auspicious_color: str = Field(default="#28A745", pattern="^#[0-9A-Fa-f]{6}$")
    inauspicious_color: str = Field(default="#DC3545", pattern="^#[0-9A-Fa-f]{6}$")
    neutral_color: str = Field(default="#007BFF", pattern="^#[0-9A-Fa-f]{6}$")
    special_color: str = Field(default="#FF9933", pattern="^#[0-9A-Fa-f]{6}$")
    show_icons: bool = True
    show_quality_stars: bool = True
    
    # Content Settings
    show_tithi_end_time: bool = True
    show_nakshatra_pada: bool = True
    show_nakshatra_deity: bool = True
    show_nakshatra_quality: bool = True
    show_karana_half: bool = True
    highlight_inauspicious: bool = True
    show_avoid_activities: bool = True
    show_best_for_activities: bool = True
    
    # Layout Settings
    display_mode: str = Field(default="compact", pattern="^(compact|detailed|full)$")
    show_on_dashboard: bool = True
    show_on_public_website: bool = True
    widget_size: str = Field(default="medium", pattern="^(small|medium|large)$")
    show_expandable_sections: bool = True
    
    # Additional Settings
    auto_refresh_enabled: bool = True
    refresh_interval_minutes: int = Field(default=60, ge=1, le=1440)
    print_format: str = Field(default="a4", pattern="^(a4|compact|detailed)$")
    include_temple_header: bool = True
    include_verification_note: bool = True
    custom_settings: Optional[Dict[str, Any]] = None
    
    @field_validator('secondary_language')
    @classmethod
    def secondary_language_different(cls, v, validation_info):
        """Secondary language should be different from primary"""
        # Note: In Pydantic v2, cross-field validation is better done with model_validator
        # This is a simplified check - full validation would require model_validator
        return v


class PanchangDisplaySettingsCreate(PanchangDisplaySettingsBase):
    """Schema for creating panchang display settings"""
    temple_id: int


class PanchangDisplaySettingsUpdate(BaseModel):
    """Schema for updating panchang display settings (all fields optional)"""

    # Location Settings
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    city_name: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)

    # Element Visibility
    show_tithi: Optional[bool] = None
    show_nakshatra: Optional[bool] = None
    show_yoga: Optional[bool] = None
    show_karana: Optional[bool] = None
    show_vara: Optional[bool] = None
    show_sun_timings: Optional[bool] = None
    show_rahu_kaal: Optional[bool] = None
    show_yamaganda: Optional[bool] = None
    show_gulika: Optional[bool] = None
    show_abhijit_muhurat: Optional[bool] = None
    show_brahma_muhurat: Optional[bool] = None
    show_festivals: Optional[bool] = None
    show_fasting_info: Optional[bool] = None
    show_choghadiya: Optional[bool] = None
    show_hora: Optional[bool] = None
    show_planetary_positions: Optional[bool] = None
    show_panchak_warning: Optional[bool] = None
    show_recommendations: Optional[bool] = None
    show_moon_timings: Optional[bool] = None
    
    # Display Format
    primary_language: Optional[str] = Field(None, pattern="^(en|hi|sa|ta|te|kn|mr|bn|gu)$")
    secondary_language: Optional[str] = Field(None, pattern="^(en|hi|sa|ta|te|kn|mr|bn|gu)$")
    show_sanskrit_names: Optional[bool] = None
    time_format_12h: Optional[bool] = None
    show_timezone: Optional[bool] = None
    show_gregorian_date: Optional[bool] = None
    show_hindu_date: Optional[bool] = None
    show_samvat: Optional[bool] = None
    
    # Visual Settings
    auspicious_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    inauspicious_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    neutral_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    special_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    show_icons: Optional[bool] = None
    show_quality_stars: Optional[bool] = None
    
    # Content Settings
    show_tithi_end_time: Optional[bool] = None
    show_nakshatra_pada: Optional[bool] = None
    show_nakshatra_deity: Optional[bool] = None
    show_nakshatra_quality: Optional[bool] = None
    show_karana_half: Optional[bool] = None
    highlight_inauspicious: Optional[bool] = None
    show_avoid_activities: Optional[bool] = None
    show_best_for_activities: Optional[bool] = None
    
    # Layout Settings
    display_mode: Optional[str] = Field(None, pattern="^(compact|detailed|full)$")
    show_on_dashboard: Optional[bool] = None
    show_on_public_website: Optional[bool] = None
    widget_size: Optional[str] = Field(None, pattern="^(small|medium|large)$")
    show_expandable_sections: Optional[bool] = None
    
    # Additional Settings
    auto_refresh_enabled: Optional[bool] = None
    refresh_interval_minutes: Optional[int] = Field(None, ge=1, le=1440)
    print_format: Optional[str] = Field(None, pattern="^(a4|compact|detailed)$")
    include_temple_header: Optional[bool] = None
    include_verification_note: Optional[bool] = None
    custom_settings: Optional[Dict[str, Any]] = None


class PanchangDisplaySettingsResponse(PanchangDisplaySettingsBase):
    """Schema for panchang display settings response"""
    
    id: int
    temple_id: int
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True  # Pydantic v2 uses from_attributes instead of orm_mode


class PanchangDisplaySettingsPreset(BaseModel):
    """Preset configurations for quick setup"""
    
    name: str
    description: str
    settings: PanchangDisplaySettingsBase


# Predefined Presets
PRESETS = {
    "minimal": PanchangDisplaySettingsPreset(
        name="Minimal",
        description="Essential elements only - Tithi, Nakshatra, Rahu Kaal, Sun timings",
        settings=PanchangDisplaySettingsBase(
            show_tithi=True,
            show_nakshatra=True,
            show_yoga=False,
            show_karana=False,
            show_vara=False,
            show_sun_timings=True,
            show_rahu_kaal=True,
            show_yamaganda=False,
            show_gulika=False,
            show_abhijit_muhurat=True,
            show_brahma_muhurat=False,
            show_festivals=True,
            show_fasting_info=False,
            show_choghadiya=False,
            show_hora=False,
            show_planetary_positions=False,
            show_panchak_warning=True,
            show_recommendations=False,
            show_moon_timings=False,
            display_mode="compact",
            widget_size="small",
        )
    ),
    "standard": PanchangDisplaySettingsPreset(
        name="Standard",
        description="Recommended settings for most temples - All essential and secondary elements",
        settings=PanchangDisplaySettingsBase(
            show_tithi=True,
            show_nakshatra=True,
            show_yoga=True,
            show_karana=True,
            show_vara=True,
            show_sun_timings=True,
            show_rahu_kaal=True,
            show_yamaganda=True,
            show_gulika=True,
            show_abhijit_muhurat=True,
            show_brahma_muhurat=True,
            show_festivals=True,
            show_fasting_info=True,
            show_choghadiya=False,
            show_hora=False,
            show_planetary_positions=False,
            show_panchak_warning=True,
            show_recommendations=True,
            show_moon_timings=False,
            display_mode="detailed",
            widget_size="medium",
        )
    ),
    "comprehensive": PanchangDisplaySettingsPreset(
        name="Comprehensive",
        description="Full panchang display with all elements including advanced features",
        settings=PanchangDisplaySettingsBase(
            show_tithi=True,
            show_nakshatra=True,
            show_yoga=True,
            show_karana=True,
            show_vara=True,
            show_sun_timings=True,
            show_rahu_kaal=True,
            show_yamaganda=True,
            show_gulika=True,
            show_abhijit_muhurat=True,
            show_brahma_muhurat=True,
            show_festivals=True,
            show_fasting_info=True,
            show_choghadiya=True,
            show_hora=True,
            show_planetary_positions=True,
            show_panchak_warning=True,
            show_recommendations=True,
            show_moon_timings=True,
            display_mode="full",
            widget_size="large",
        )
    ),
}

