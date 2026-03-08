import io

from sqlalchemy.orm import Session

from app.models.donation import Donation, DonationType
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


def generate_receipt_pdf(donation: Donation, db: Session):
    """Generate PDF receipt buffer for a donation."""
    print(f"[RECEIPT PDF] Starting PDF generation for donation {donation.id}")
    try:
        from datetime import datetime
        import os
        import requests
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        print(f"[RECEIPT PDF] All imports successful")

        temple = None
        temple_logo_path = None
        if donation.temple_id:
            temple = db.query(Temple).filter(Temple.id == donation.temple_id).first()
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

        devotee = donation.devotee if hasattr(donation, "devotee") else None
        category = donation.category if hasattr(donation, "category") else None

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

        elements.append(Paragraph("DONATION RECEIPT", title_style))
        elements.append(Spacer(1, 0.2 * inch))

        receipt_number = (
            donation.receipt_number
            if hasattr(donation, "receipt_number") and donation.receipt_number
            else "N/A"
        )
        donation_date_str = ""
        if hasattr(donation, "donation_date") and donation.donation_date:
            try:
                if hasattr(donation.donation_date, "strftime"):
                    donation_date_str = donation.donation_date.strftime("%d-%m-%Y")
                else:
                    donation_date_str = str(donation.donation_date)
            except Exception:
                donation_date_str = str(donation.donation_date) if donation.donation_date else ""

        receipt_data = [
            ["Receipt Number:", receipt_number],
            ["Date:", donation_date_str],
            [
                "Devotee Name:",
                devotee.name if devotee and hasattr(devotee, "name") else "Anonymous",
            ],
            ["Phone:", devotee.phone if devotee and hasattr(devotee, "phone") else "N/A"],
            [
                "Address:",
                devotee.address
                if devotee and hasattr(devotee, "address") and devotee.address
                else "N/A",
            ],
            ["Category:", category.name if category and hasattr(category, "name") else "N/A"],
        ]

        donation_type_value = donation.donation_type
        print(f"[RECEIPT PDF] donation_type_value: {donation_type_value}, type: {type(donation_type_value)}")

        if isinstance(donation_type_value, str):
            is_in_kind = donation_type_value.lower() == "in_kind"
            print(f"[RECEIPT PDF] Detected as string, is_in_kind: {is_in_kind}")
        elif isinstance(donation_type_value, DonationType):
            is_in_kind = donation_type_value == DonationType.IN_KIND
            print(f"[RECEIPT PDF] Detected as enum, is_in_kind: {is_in_kind}")
        else:
            is_in_kind = str(donation_type_value).lower() == "in_kind"
            print(f"[RECEIPT PDF] Using fallback comparison, is_in_kind: {is_in_kind}")

        if is_in_kind:
            receipt_data.append(["Donation Type:", "In-Kind Donation"])
            if hasattr(donation, "item_name") and donation.item_name:
                receipt_data.append(["Item Name:", str(donation.item_name)])
            if hasattr(donation, "item_description") and donation.item_description:
                receipt_data.append(["Item Description:", str(donation.item_description)])
            if (
                hasattr(donation, "quantity")
                and hasattr(donation, "unit")
                and donation.quantity
                and donation.unit
            ):
                receipt_data.append(["Quantity:", f"{donation.quantity} {donation.unit}"])
            if hasattr(donation, "purity") and donation.purity:
                receipt_data.append(["Purity:", str(donation.purity)])
            if hasattr(donation, "weight_gross") and donation.weight_gross:
                receipt_data.append(["Weight (Gross):", f"{donation.weight_gross} grams"])
            if hasattr(donation, "weight_net") and donation.weight_net:
                receipt_data.append(["Weight (Net):", f"{donation.weight_net} grams"])
            receipt_data.append(["Assessed Value:", f"₹ {donation.amount:,.2f}"])
        else:
            payment_mode_display = donation.payment_mode.upper() if donation.payment_mode else "Cash"
            receipt_data.append(["Payment Mode:", payment_mode_display])
            receipt_data.append(["Amount:", f"₹ {donation.amount:,.2f}"])

        if category and category.is_80g_eligible and temple and temple.certificate_80g_number:
            receipt_data.append(["80G Certificate:", f"Yes - {temple.certificate_80g_number}"])
            receipt_data.append(["80G Valid From:", temple.certificate_80g_valid_from or "N/A"])
            receipt_data.append(["80G Valid To:", temple.certificate_80g_valid_to or "N/A"])

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

        try:
            amount_int = int(donation.amount) if donation.amount else 0
            amount_words = f"Rupees {number_to_words(amount_int)} Only"
            elements.append(Paragraph(f"<b>Amount in Words:</b> {amount_words}", styles["Normal"]))
        except (ValueError, TypeError):
            elements.append(Paragraph(f"<b>Amount:</b> ₹ {donation.amount:,.2f}", styles["Normal"]))
        elements.append(Spacer(1, 0.3 * inch))

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
                Paragraph(
                    f"Authorized Signatory: {temple.authorized_signatory_name}", styles["Normal"]
                )
            )
            if temple.authorized_signatory_designation:
                elements.append(Paragraph(temple.authorized_signatory_designation, styles["Normal"]))

        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", footer_style))
        elements.append(Paragraph("MandirMitra Temple Management System", footer_style))

        print(f"[RECEIPT PDF] Building PDF document with {len(elements)} elements...")
        doc.build(elements)
        buffer.seek(0)
        print(f"[RECEIPT PDF] PDF built successfully, buffer size: {len(buffer.getvalue())} bytes")

        return buffer
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"[RECEIPT PDF] ===== CRITICAL ERROR IN PDF GENERATION =====")
        print(f"[RECEIPT PDF] Error type: {type(e).__name__}")
        print(f"[RECEIPT PDF] Error message: {str(e)}")
        print(f"[RECEIPT PDF] Full traceback:\n{error_details}")
        print(f"[RECEIPT PDF] ===== END ERROR =====")
        raise
