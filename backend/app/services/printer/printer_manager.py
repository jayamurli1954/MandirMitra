"""
Printer Manager for MandirMitra
Handles Thermal (USB/Network) and Standard (OS/Inkjet/Laser) printers.
"""

import logging
import yaml
import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Dict, Optional, Union
from datetime import datetime

# Attempt to import escpos, but don't fail if USB/drivers are missing
try:
    from escpos.printer import Usb, Network, Dummy

    ESCPOS_AVAILABLE = True
except ImportError:
    ESCPOS_AVAILABLE = False
    print("WARNING: python-escpos not found. Thermal printing will be disabled.")

try:
    import win32print
    import win32api

    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

logger = logging.getLogger(__name__)


class OSPrinter:
    """
    Wrapper for Standard OS Printers (Inkjet, Laser, Dot Matrix)
    Uses the OS command to print a PDF or Text file.
    """

    def __init__(self, name: str, printer_type: str = "os_printer"):
        self.name = name
        self.printer_type = printer_type

    def print_file(self, file_path: str):
        """Send a file (PDF/Text) to the OS printer"""
        try:
            abs_path = os.path.abspath(file_path)
            if not os.path.exists(abs_path):
                logger.error(f"File not found: {abs_path}")
                return False

            system = platform.system()
            if system == "Windows":
                # Use ShellExecute to print
                # This uses the "print" verb associated with the file type
                win32api.ShellExecute(0, "printto", abs_path, f'"{self.name}"', ".", 0)
                return True
            else:
                # Linux/Mac (lp command)
                subprocess.run(["lp", "-d", self.name, abs_path], check=True)
                return True
        except Exception as e:
            logger.error(f"Error printing to OS printer {self.name}: {e}")
            return False


class PrinterManager:
    """
    Manages all configured printers.
    """

    def __init__(self, config_path: str = "printer_config.yaml"):
        # Resolve config path relative to backend root
        base_path = Path(__file__).parent.parent.parent.parent
        self.config_path = base_path / config_path
        self.config = self._load_config()
        self.printers: Dict[str, any] = {}
        self.initialize_printers()

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            logger.warning(f"Printer config not found at {self.config_path}")
            return {"printers": {}}

        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def initialize_printers(self):
        """Initialize connection to all enabled printers"""
        logger.info("Initializing printers...")

        printers_conf = self.config.get("printers", {})

        for p_id, p_conf in printers_conf.items():
            if not p_conf.get("enabled", False):
                continue

            p_type = p_conf.get("type")

            try:
                if p_type == "os_printer":
                    printer_name = p_conf["connection"]["printer_name"]
                    self.printers[p_id] = OSPrinter(printer_name)
                    logger.info(f"Initialized OS Printer: {p_id} ({printer_name})")

                elif p_type in ["thermal_usb", "thermal_network"]:
                    if not ESCPOS_AVAILABLE:
                        logger.error(f"Cannot init {p_id}: python-escpos not installed")
                        continue

                    connection = p_conf["connection"]
                    if p_type == "thermal_usb":
                        # Note: This requires Zadig/libusb driver on Windows
                        vendor = int(str(connection["vendor_id"]), 16)
                        product = int(str(connection["product_id"]), 16)
                        self.printers[p_id] = Usb(
                            vendor, product, profile=connection.get("profile", "default")
                        )

                    elif p_type == "thermal_network":
                        self.printers[p_id] = Network(
                            host=connection["host"], port=connection.get("port", 9100)
                        )

                    logger.info(f"Initialized Thermal Printer: {p_id}")

            except Exception as e:
                logger.error(f"Failed to initialize printer {p_id}: {e}")

    def get_printer(self, printer_id: str):
        return self.printers.get(printer_id)

    def get_default_printer_id(self) -> Optional[str]:
        """Get the default printer ID from config"""
        return self.config.get("settings", {}).get("default_printer_id")

    def print_ticket(self, printer_id: str, data: dict):
        """
        High-level print function.
        Handles formatting based on printer type.
        """
        printer = self.get_printer(printer_id)
        if not printer:
            logger.error(f"Printer {printer_id} not found or not initialized")
            return False

        try:
            if isinstance(printer, OSPrinter):
                # For OS Printer, generate PDF and print
                from .print_templates import generate_ticket_pdf

                pdf_path = generate_ticket_pdf(data)
                if pdf_path:
                    printer.print_file(pdf_path)
                    return True
            else:
                # For Thermal, use ESC/POS commands
                from .print_templates import print_ticket_thermal

                print_ticket_thermal(printer, data)
                return True

        except Exception as e:
            logger.error(f"Print job failed for {printer_id}: {e}")
            return False

        return False


# Global Instance
_printer_manager = None


def get_printer_manager():
    global _printer_manager
    if _printer_manager is None:
        _printer_manager = PrinterManager()
    return _printer_manager
