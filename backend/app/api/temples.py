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
        temple = db.query(Temple).filter(Temple.id == current_user.temple_id).first()
        if temple:
            return [temple]
    return []


@router.get("/{temple_id}", response_model=TempleResponse)
def get_temple(
    temple_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get temple details"""
    temple = db.query(Temple).filter(
        Temple.id == temple_id,
        Temple.id == current_user.temple_id  # Ensure user can only access their temple
    ).first()
    
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
    
    temple = db.query(Temple).filter(Temple.id == current_user.temple_id).first()
    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")
    
    return {
        "module_donations_enabled": temple.module_donations_enabled if hasattr(temple, 'module_donations_enabled') else True,
        "module_sevas_enabled": temple.module_sevas_enabled if hasattr(temple, 'module_sevas_enabled') else True,
        "module_inventory_enabled": temple.module_inventory_enabled if hasattr(temple, 'module_inventory_enabled') else True,
        "module_assets_enabled": temple.module_assets_enabled if hasattr(temple, 'module_assets_enabled') else True,
        "module_accounting_enabled": temple.module_accounting_enabled if hasattr(temple, 'module_accounting_enabled') else True,
        "module_tender_enabled": temple.module_tender_enabled if hasattr(temple, 'module_tender_enabled') else False,
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
        "module_panchang_enabled": temple.module_panchang_enabled if hasattr(temple, 'module_panchang_enabled') else True,
        "module_reports_enabled": temple.module_reports_enabled if hasattr(temple, 'module_reports_enabled') else True,
        "module_token_seva_enabled": temple.module_token_seva_enabled if hasattr(temple, 'module_token_seva_enabled') else True,
    }

