"""
Temple Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.temple import Temple
from app.models.user import User

router = APIRouter(prefix="/api/v1/temples", tags=["temples"])


class TempleResponse(BaseModel):
    """Temple response schema"""
    id: int
    name: str
    slug: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    # Module Configuration
    module_donations_enabled: bool = True
    module_sevas_enabled: bool = True
    module_inventory_enabled: bool = True
    module_assets_enabled: bool = True
    module_accounting_enabled: bool = True
    module_tender_enabled: bool = False
    module_panchang_enabled: bool = True
    module_reports_enabled: bool = True
    module_token_seva_enabled: bool = True
    
    class Config:
        from_attributes = True


class ModuleConfigUpdate(BaseModel):
    """Schema for updating module configuration"""
    module_donations_enabled: Optional[bool] = None
    module_sevas_enabled: Optional[bool] = None
    module_inventory_enabled: Optional[bool] = None
    module_assets_enabled: Optional[bool] = None
    module_accounting_enabled: Optional[bool] = None
    module_tender_enabled: Optional[bool] = None
    module_hr_enabled: Optional[bool] = None
    module_hundi_enabled: Optional[bool] = None
    module_panchang_enabled: Optional[bool] = None
    module_reports_enabled: Optional[bool] = None
    module_token_seva_enabled: Optional[bool] = None


@router.get("/", response_model=List[TempleResponse])
def get_temples(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get temples (for current user's temple)"""
    if current_user.temple_id:
        # Use raw SQL to avoid missing column errors (module_hundi_enabled may not exist in DB)
        from sqlalchemy import text
        
        # Check if module_hundi_enabled column exists first
        column_check = db.execute(
            text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'temples' AND column_name = 'module_hundi_enabled'
            """)
        ).fetchone()
        
        has_hundi_column = column_check is not None
        
        # Build query based on whether column exists
        if has_hundi_column:
            # Query all columns including module_hundi_enabled
            result = db.execute(
                text("SELECT * FROM temples WHERE id = :temple_id"),
                {"temple_id": current_user.temple_id}
            ).fetchone()
        else:
            # Query without module_hundi_enabled column
            result = db.execute(
                text("""
                    SELECT id, name, name_kannada, name_sanskrit, slug, primary_deity, 
                           deity_name_kannada, deity_name_sanskrit, address, city, state, pincode,
                           phone, email, website, registration_number, trust_name, pan_number, tan_number,
                           certificate_80g_number, certificate_80g_valid_from, certificate_80g_valid_to,
                           certificate_12a_number, certificate_12a_valid_from, fcra_applicable,
                           fcra_registration_number, fcra_valid_from, fcra_valid_to, fcra_bank_account_id,
                           gst_applicable, gstin, gst_registration_date, gst_tax_rates,
                           bank_name, bank_account_number, bank_ifsc_code, bank_branch, bank_account_type,
                           upi_id, bank_name_2, bank_account_number_2, bank_ifsc_code_2,
                           financial_year_start_month, receipt_prefix_donation, receipt_prefix_seva,
                           receipt_prefix_sponsorship, receipt_prefix_inkind, token_seva_threshold,
                           module_donations_enabled, module_sevas_enabled, module_inventory_enabled,
                           module_assets_enabled, module_accounting_enabled, module_tender_enabled,
                           module_hr_enabled, module_panchang_enabled, module_reports_enabled,
                           module_token_seva_enabled, chairman_name, chairman_phone, chairman_email,
                           authorized_signatory_name, authorized_signatory_designation, signature_image_url,
                           opening_time, closing_time, logo_url, banner_url, description, is_active,
                           created_at, updated_at
                    FROM temples 
                    WHERE id = :temple_id
                """),
                {"temple_id": current_user.temple_id}
            ).fetchone()
        
        if result:
            # If column exists, use normal query
            if has_hundi_column:
                temple = db.query(Temple).filter(Temple.id == current_user.temple_id).first()
                if temple:
                    return [temple]
            else:
                # Column doesn't exist - create a minimal Temple object with default value
                # Use raw SQL result and manually construct response
                temple = db.query(Temple).filter(Temple.id == current_user.temple_id).first()
                if temple:
                    # Dynamically add the missing attribute
                    setattr(temple, 'module_hundi_enabled', True)
                    return [temple]
    return []


@router.get("/{temple_id}", response_model=TempleResponse)
def get_temple(
    temple_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get temple details"""
    # Use raw SQL to avoid missing column errors
    from sqlalchemy import text
    # Check if module_hundi_enabled column exists first
    column_check = db.execute(
        text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'temples' AND column_name = 'module_hundi_enabled'
        """)
    ).fetchone()
    
    has_hundi_column = column_check is not None
    
    if has_hundi_column:
        temple = db.query(Temple).filter(
            Temple.id == temple_id,
            Temple.id == current_user.temple_id
        ).first()
    else:
        # Query without module_hundi_enabled
        result = db.execute(
            text("""
                SELECT id, name, slug, address, city, state, phone, email, 
                       module_donations_enabled, module_sevas_enabled, module_inventory_enabled,
                       module_assets_enabled, module_accounting_enabled, module_tender_enabled,
                       module_hr_enabled, module_panchang_enabled, module_reports_enabled,
                       module_token_seva_enabled
                FROM temples 
                WHERE id = :temple_id
            """),
            {"temple_id": temple_id}
        ).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Temple not found")
        
        # Create a minimal temple object
        temple = db.query(Temple).filter(Temple.id == temple_id).first()
        if temple:
            # Set default for missing column
            temple.module_hundi_enabled = True
    
    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")
    
    return temple


@router.get("/modules/config", response_model=dict)
def get_module_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get module configuration for current temple"""
    if not current_user.temple_id:
        raise HTTPException(status_code=404, detail="Temple not found")
    
    # Use raw SQL to avoid missing column errors (module_hundi_enabled may not exist in DB)
    from sqlalchemy import text
    # Check if module_hundi_enabled column exists first
    column_check = db.execute(
        text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'temples' AND column_name = 'module_hundi_enabled'
        """)
    ).fetchone()
    
    has_hundi_column = column_check is not None
    
    if has_hundi_column:
        result = db.execute(
            text("""
                SELECT 
                    id, name,
                    COALESCE(module_donations_enabled, true) as module_donations_enabled,
                    COALESCE(module_sevas_enabled, true) as module_sevas_enabled,
                    COALESCE(module_inventory_enabled, true) as module_inventory_enabled,
                    COALESCE(module_assets_enabled, true) as module_assets_enabled,
                    COALESCE(module_accounting_enabled, true) as module_accounting_enabled,
                    COALESCE(module_tender_enabled, false) as module_tender_enabled,
                    COALESCE(module_hr_enabled, true) as module_hr_enabled,
                    COALESCE(module_hundi_enabled, true) as module_hundi_enabled,
                    COALESCE(module_panchang_enabled, true) as module_panchang_enabled,
                    COALESCE(module_reports_enabled, true) as module_reports_enabled,
                    COALESCE(module_token_seva_enabled, true) as module_token_seva_enabled
                FROM temples 
                WHERE id = :temple_id
            """),
            {"temple_id": current_user.temple_id}
        ).fetchone()
    else:
        result = db.execute(
            text("""
                SELECT 
                    id, name,
                    COALESCE(module_donations_enabled, true) as module_donations_enabled,
                    COALESCE(module_sevas_enabled, true) as module_sevas_enabled,
                    COALESCE(module_inventory_enabled, true) as module_inventory_enabled,
                    COALESCE(module_assets_enabled, true) as module_assets_enabled,
                    COALESCE(module_accounting_enabled, true) as module_accounting_enabled,
                    COALESCE(module_tender_enabled, false) as module_tender_enabled,
                    COALESCE(module_hr_enabled, true) as module_hr_enabled,
                    true as module_hundi_enabled,
                    COALESCE(module_panchang_enabled, true) as module_panchang_enabled,
                    COALESCE(module_reports_enabled, true) as module_reports_enabled,
                    COALESCE(module_token_seva_enabled, true) as module_token_seva_enabled
                FROM temples 
                WHERE id = :temple_id
            """),
            {"temple_id": current_user.temple_id}
        ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Temple not found")
    
    # Create a simple object to mimic the temple object
    class SimpleTemple:
        def __init__(self, row):
            self.id = row[0]
            self.name = row[1]
            self.module_donations_enabled = row[2]
            self.module_sevas_enabled = row[3]
            self.module_inventory_enabled = row[4]
            self.module_assets_enabled = row[5]
            self.module_accounting_enabled = row[6]
            self.module_tender_enabled = row[7]
            self.module_hr_enabled = row[8]
            self.module_hundi_enabled = row[9]
            self.module_panchang_enabled = row[10]
            self.module_reports_enabled = row[11]
            self.module_token_seva_enabled = row[12]
    
    temple = SimpleTemple(result)
    
    return {
        "module_donations_enabled": temple.module_donations_enabled if hasattr(temple, 'module_donations_enabled') else True,
        "module_sevas_enabled": temple.module_sevas_enabled if hasattr(temple, 'module_sevas_enabled') else True,
        "module_inventory_enabled": temple.module_inventory_enabled if hasattr(temple, 'module_inventory_enabled') else True,
        "module_assets_enabled": temple.module_assets_enabled if hasattr(temple, 'module_assets_enabled') else True,
        "module_accounting_enabled": temple.module_accounting_enabled if hasattr(temple, 'module_accounting_enabled') else True,
        "module_tender_enabled": temple.module_tender_enabled if hasattr(temple, 'module_tender_enabled') else False,
        "module_hr_enabled": temple.module_hr_enabled if hasattr(temple, 'module_hr_enabled') else True,
        "module_hundi_enabled": temple.module_hundi_enabled if hasattr(temple, 'module_hundi_enabled') else True,
        "module_panchang_enabled": temple.module_panchang_enabled if hasattr(temple, 'module_panchang_enabled') else True,
        "module_reports_enabled": temple.module_reports_enabled if hasattr(temple, 'module_reports_enabled') else True,
        "module_token_seva_enabled": temple.module_token_seva_enabled if hasattr(temple, 'module_token_seva_enabled') else True,
    }


@router.put("/modules/config", response_model=dict)
def update_module_config(
    config: ModuleConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update module configuration for current temple"""
    if not current_user.temple_id:
        raise HTTPException(status_code=404, detail="Temple not found")
    
    temple = db.query(Temple).filter(Temple.id == current_user.temple_id).first()
    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")
    
    # Update only provided fields
    update_data = config.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(temple, field):
            setattr(temple, field, value)
    
    db.commit()
    db.refresh(temple)
    
    return {
        "module_donations_enabled": temple.module_donations_enabled if hasattr(temple, 'module_donations_enabled') else True,
        "module_sevas_enabled": temple.module_sevas_enabled if hasattr(temple, 'module_sevas_enabled') else True,
        "module_inventory_enabled": temple.module_inventory_enabled if hasattr(temple, 'module_inventory_enabled') else True,
        "module_assets_enabled": temple.module_assets_enabled if hasattr(temple, 'module_assets_enabled') else True,
        "module_accounting_enabled": temple.module_accounting_enabled if hasattr(temple, 'module_accounting_enabled') else True,
        "module_tender_enabled": temple.module_tender_enabled if hasattr(temple, 'module_tender_enabled') else False,
        "module_hr_enabled": temple.module_hr_enabled if hasattr(temple, 'module_hr_enabled') else True,
        "module_hundi_enabled": temple.module_hundi_enabled if hasattr(temple, 'module_hundi_enabled') else True,
        "module_panchang_enabled": temple.module_panchang_enabled if hasattr(temple, 'module_panchang_enabled') else True,
        "module_reports_enabled": temple.module_reports_enabled if hasattr(temple, 'module_reports_enabled') else True,
        "module_token_seva_enabled": temple.module_token_seva_enabled if hasattr(temple, 'module_token_seva_enabled') else True,
    }

