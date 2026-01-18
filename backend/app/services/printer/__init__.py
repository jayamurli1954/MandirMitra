"""
Printer service module for MandirMitra
Handles printing functionality for receipts and reports
"""

from .print_queue import get_print_queue, PrintJob
from .printer_manager import get_printer_manager

__all__ = [
    "get_print_queue",
    "PrintJob",
    "get_printer_manager",
]
