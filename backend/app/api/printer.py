from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel
from app.services.printer.printer_manager import get_printer_manager
from app.services.printer.print_queue import get_print_queue
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/printers", tags=["Printers"])


class PrinterStatus(BaseModel):
    id: str
    type: str
    name: str


class PrintRequest(BaseModel):
    printer_id: str
    data: dict


def _require_printer_access(current_user: User) -> None:
    allowed_roles = {"admin", "super_admin", "temple_manager", "counter_staff", "accountant"}
    if current_user.role not in allowed_roles and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to printer operations",
        )


@router.get("/", response_model=List[PrinterStatus])
def get_printers(current_user: User = Depends(get_current_user)):
    """List all configured printers"""
    _require_printer_access(current_user)
    manager = get_printer_manager()
    # Re-initialize to check for new connections/config changes if needed?
    # For now, just return loaded config.
    printers = []
    for p_id, p_obj in manager.printers.items():
        p_type = "unknown"
        p_name = "Unknown"

        # Determine type/name based on object class
        if hasattr(p_obj, "name"):  # OSPrinter
            p_name = p_obj.name
            p_type = getattr(p_obj, "printer_type", "os_printer")
        elif hasattr(p_obj, "idVendor"):  # Usb
            p_name = f"USB Printer {hex(p_obj.idVendor)}:{hex(p_obj.idProduct)}"
            p_type = "thermal_usb"
        elif hasattr(p_obj, "host"):  # Network
            p_name = f"Net Printer {p_obj.host}"
            p_type = "thermal_network"

        printers.append(PrinterStatus(id=p_id, type=p_type, name=p_name))
    return printers


@router.post("/print")
def print_ticket(request: PrintRequest, current_user: User = Depends(get_current_user)):
    """Enqueue a print job"""
    _require_printer_access(current_user)
    queue = get_print_queue()
    job_id = queue.add_job(request.printer_id, request.data)
    return {"status": "queued", "job_id": job_id}


@router.get("/discover")
def discover_usb(current_user: User = Depends(get_current_user)):
    """Discover connected USB printers (Helper for config)"""
    _require_printer_access(current_user)
    try:
        import usb.core

        devices = []
        # Find all USB devices (filtering for printer class 0x07 would be better but simple scan first)
        for dev in usb.core.find(find_all=True):
            # Printer Class is usually 7
            if dev.bDeviceClass == 7 or True:  # Listing all for debug
                try:
                    devices.append(
                        {
                            "vendor_id": hex(dev.idVendor),
                            "product_id": hex(dev.idProduct),
                            "class": dev.bDeviceClass,
                        }
                    )
                except:
                    pass
        return devices
    except ImportError:
        return {"error": "pyusb/libusb not available"}
