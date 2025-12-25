from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.services.printer import get_printer_manager
from app.services.printer import get_print_queue

router = APIRouter(prefix="/api/v1/printers", tags=["Printers"])


class PrinterStatus(BaseModel):
    id: str
    type: str
    name: str


class PrintRequest(BaseModel):
    printer_id: str
    data: dict


@router.get("/", response_model=List[PrinterStatus])
def get_printers():
    """List all configured printers"""
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
def print_ticket(request: PrintRequest):
    """Enqueue a print job"""
    queue = get_print_queue()
    job_id = queue.add_job(request.printer_id, request.data)
    return {"status": "queued", "job_id": job_id}


@router.get("/discover")
def discover_usb():
    """Discover connected USB printers (Helper for config)"""
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
