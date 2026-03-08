import io
import os
from datetime import datetime

import requests
from sqlalchemy.orm import Session

from app.models.seva import Seva, SevaBooking, SevaBookingStatus
from app.models.temple import Temple


def number_to_words(n):
    """Convert number to words (simple implementation)."""
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    teens = [
        "Ten",
        "Eleven",
        "Twelve",
        "Thirteen",
        "Fourteen",
        "Fifteen",
        "Sixteen",
        "Seventeen",
        "Eighteen",
        "Nineteen",
    ]

    if n == 0:
        return "Zero"

    def convert_hundreds(num):
        result = ""
        if num >= 100:
            result += ones[num // 100] + " Hundred "
            num %= 100
        if num >= 20:
            result += tens[num // 10] + " "
            num %= 10
        elif num >= 10:
            result += teens[num - 10] + " "
            return result
        if num > 0:
            result += ones[num] + " "
        return result

    result = ""
    if n >= 10000000:
        result += convert_hundreds(n // 10000000) + "Crore "
        n %= 10000000
    if n >= 100000:
        result += convert_hundreds(n // 100000) + "Lakh "
        n %= 100000
    if n >= 1000:
        result += convert_hundreds(n // 1000) + "Thousand "
        n %= 1000
    if n > 0:
        result += convert_hundreds(n)

    return result.strip()


def generate_seva_receipt_pdf(booking: SevaBooking, db: Session, temple_id: int = None):
    """Generate PDF receipt buffer for a seva booking."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    temple = None
    temple_logo_path = None

    if not temple_id:
        if booking.devotee and hasattr(booking.devotee, "temple_id"):
            temple_id = booking.devotee.temple_id
        elif booking.user and hasattr(booking.user, "temple_id"):
            temple_id = booking.user.temple_id

    if temple_id:
        temple = db.query(Temple).filter(Temple.id == temple_id).first()
        if temple and temple.logo_url:
            try:
                if temple.logo_url.startswith("http"):
                    response = requests.get(temple.logo_url, timeout=5)
                    if response.status_code == 200:
                        temple_logo_path = io.BytesIO(response.content)
                elif os.path.exists(temple.logo_url):
                    temple_logo_path = temple.logo_url
            except Exception:
                temple_logo_path = None

    devotee = booking.devotee if hasattr(booking, "devotee") else None
    seva = booking.seva if hasattr(booking, "seva") else None

    if not seva and hasattr(booking, "seva_id") and booking.seva_id:
        seva = db.query(Seva).filter(Seva.id == booking.seva_id).first()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    elements = []

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReceiptTitle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#FF9933"),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )

    header_style = ParagraphStyle(
        "ReceiptHeader",
        parent=styles["Normal"],
        fontSize=14,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    if temple:
        if temple_logo_path:
            try:
                logo = Image(temple_logo_path, width=1.2 * inch, height=1.2 * inch)
                logo.hAlign = "CENTER"
                elements.append(logo)
                elements.append(Spacer(1, 0.1 * inch))
            except Exception:
                pass

        if temple.name:
            elements.append(Paragraph(temple.name, title_style))

        if temple.address:
            elements.append(Paragraph(temple.address, header_style))

        if temple.phone:
            elements.append(Paragraph(f"Phone: {temple.phone}", styles["Normal"]))

        if temple.email:
            elements.append(Paragraph(f"Email: {temple.email}", styles["Normal"]))

        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph("_" * 80, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("SEVA BOOKING RECEIPT", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    receipt_date = booking.created_at.date() if booking.created_at else None
    receipt_data = [
        ["Receipt Number:", booking.receipt_number or f"SEV{booking.id}"],
        ["Receipt Date:", receipt_date.strftime("%d-%m-%Y") if receipt_date else ""],
        ["Seva Date:", booking.booking_date.strftime("%d-%m-%Y") if booking.booking_date else ""],
        ["Seva Time:", booking.booking_time or "All Day"],
        ["Seva Name:", seva.name_english if seva else "N/A"],
        ["Devotee Name:", devotee.name if devotee else "N/A"],
        ["Phone:", devotee.phone if devotee else "N/A"],
        ["Address:", devotee.address if devotee and devotee.address else "N/A"],
        ["Payment Mode:", booking.payment_method.upper() if booking.payment_method else "Cash"],
        ["Amount Paid:", f"Rs. {booking.amount_paid:,.2f}"],
    ]

    if booking.reschedule_requested_date:
        original_date = booking.original_booking_date or booking.booking_date
        if booking.reschedule_approved is True:
            approval_status = "Approved"
        elif booking.reschedule_approved is False:
            approval_status = "Rejected"
        else:
            approval_status = "Pending"

        receipt_data.append(["Original Date:", original_date.strftime("%d-%m-%Y") if original_date else ""])
        receipt_data.append([
            "Requested Reschedule Date:",
            booking.reschedule_requested_date.strftime("%d-%m-%Y"),
        ])
        receipt_data.append(["Approval Status:", approval_status])

    if booking.gotra:
        receipt_data.append(["Gotra:", booking.gotra])
    if booking.nakshatra:
        receipt_data.append(["Nakshatra:", booking.nakshatra])
    if booking.rashi:
        receipt_data.append(["Rashi:", booking.rashi])
    if booking.special_request:
        receipt_data.append(["Special Request:", booking.special_request])
    if booking.payment_method == "UPI" and booking.upi_reference_number:
        receipt_data.append(["UPI Reference:", booking.upi_reference_number])
    if booking.payment_method == "Cheque" and booking.cheque_number:
        receipt_data.append(["Cheque Number:", booking.cheque_number])
        if booking.cheque_bank_name:
            receipt_data.append(["Bank Name:", booking.cheque_bank_name])
    if booking.payment_method == "Online" and booking.utr_number:
        receipt_data.append(["UTR Number:", booking.utr_number])

    receipt_table = Table(receipt_data, colWidths=[2.5 * inch, 4 * inch])
    receipt_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )

    elements.append(receipt_table)
    elements.append(Spacer(1, 0.3 * inch))

    amount_words = f"Rupees {number_to_words(int(booking.amount_paid))} Only"
    elements.append(Paragraph(f"<b>Amount in Words:</b> {amount_words}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    status_note = ""
    if booking.status == SevaBookingStatus.PENDING:
        status_note = "This booking is pending approval."
    elif booking.status == SevaBookingStatus.CONFIRMED:
        status_note = "This booking is confirmed. Please arrive on time."
    elif booking.status == SevaBookingStatus.COMPLETED:
        status_note = "This seva has been completed."
    elif booking.status == SevaBookingStatus.CANCELLED:
        status_note = "This booking has been cancelled."

    if status_note:
        elements.append(Paragraph(f"<b>Status:</b> {status_note}", styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    footer_style = ParagraphStyle(
        "ReceiptFooter",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )

    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("_" * 80, styles["Normal"]))
    elements.append(Spacer(1, 0.1 * inch))

    if temple and temple.authorized_signatory_name:
        elements.append(
            Paragraph(f"Authorized Signatory: {temple.authorized_signatory_name}", styles["Normal"])
        )
        if temple.authorized_signatory_designation:
            elements.append(Paragraph(temple.authorized_signatory_designation, styles["Normal"]))

    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", footer_style))
    elements.append(Paragraph("MandirMitra Temple Management System", footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

