"""
Print Templates for MandirMitra
Handles layout for Thermal (ESC/POS) and PDF (Standard) outputs.
"""

import os
import tempfile
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import mm


def print_ticket_thermal(printer, data: dict):
    """
    Print a Seva Token/Ticket on a thermal printer using ESC/POS
    """
    # Header
    printer.set(align="center", text_type="B", width=2, height=2)
    printer.text(f"{data.get('temple_name', 'MANDIR')}\n")
    printer.set(text_type="normal", width=1, height=1)
    printer.text(f"{data.get('temple_city', '')}\n")
    printer.text("-" * 32 + "\n\n")

    # Token Info
    printer.set(align="center", text_type="B", width=3, height=3)
    printer.text(f"TOKEN: {data['token']}\n\n")

    # Details
    printer.set(align="left", text_type="normal", width=1, height=1)
    printer.text(f"Seva:   {data['seva_name']}\n")
    printer.text(f"Date:   {data['date']}\n")
    printer.text(f"Time:   {data['time']}\n")
    printer.text(f"Amount: Rs.{data['amount']}\n\n")

    # Devotee
    printer.set(align="left", text_type="B")
    printer.text(f"Devotee: {data['devotee_name']}\n\n")

    # Booking ID / QR
    printer.set(align="center", text_type="normal")
    if "booking_id" in data:
        try:
            # Note: native qr implementation varies by printer library version
            printer.qr(data["booking_id"], size=8)
        except:
            printer.text(f"[QR: {data['booking_id']}]\n")

    printer.text(f"\nID: {data['booking_id']}\n")

    # Footer
    printer.text("-" * 32 + "\n")
    printer.text(f"Issued: {datetime.now().strftime('%d-%b-%Y %H:%M')}\n")
    printer.text("Please wait for your turn.\n\n\n")

    printer.cut()


def generate_ticket_pdf(data: dict) -> str:
    """
    Generate a PDF ticket for standard printers.
    Returns the absolute path to the generated temp PDF file.
    """
    # Create temp file
    fd, path = tempfile.mkstemp(suffix=".pdf", prefix="ticket_")
    os.close(fd)

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    # Draw simple ticket layout (Top-Left of A4 or centered)
    # Let's make it look like a receipt in the center

    x_start = 50 * mm
    y_start = height - 50 * mm

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y_start, data.get("temple_name", "MANDIR"))

    y = y_start - 20
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, y, data.get("temple_city", ""))

    y -= 40
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, y, f"TOKEN: {data['token']}")

    y -= 40
    c.setFont("Helvetica", 12)
    c.drawString(x_start, y, f"Seva: {data['seva_name']}")
    y -= 20
    c.drawString(x_start, y, f"Date: {data['date']}  |  Time: {data['time']}")
    y -= 20
    c.drawString(x_start, y, f"Devotee: {data['devotee_name']}")
    y -= 20
    c.drawString(x_start, y, f"Amount: Rs. {data['amount']}")

    y -= 40
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, y, f"Booking ID: {data['booking_id']}")

    y -= 20
    c.drawCentredString(width / 2, y, f"Issued: {datetime.now().strftime('%d-%b-%Y %H:%M')}")

    c.save()
    return path
