"""
Donation API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, date
import io
import csv
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as ExcelImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os
import requests
from urllib.parse import urlparse

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.donation import Donation, DonationCategory
from app.models.devotee import Devotee
from app.models.temple import Temple
from app.models.user import User
from app.models.accounting import Account, JournalEntry, JournalLine
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/donations", tags=["donations"])


def post_donation_to_accounting(db: Session, donation: Donation, temple_id: int):
    """
    Create journal entry for donation in accounting system
    Dr: Cash/Bank Account (based on payment mode)
    Cr: Donation Income Account (based on payment mode)
    """
    try:
        # Determine debit account (payment method)
        debit_account_code = None
        if donation.payment_mode.upper() in ['CASH', 'COUNTER']:
            debit_account_code = '1101'  # Cash in Hand - Counter
        elif donation.payment_mode.upper() in ['UPI', 'ONLINE', 'CARD', 'NETBANKING']:
            debit_account_code = '1110'  # Bank - SBI Current Account
        elif 'HUNDI' in donation.payment_mode.upper():
            debit_account_code = '1102'  # Cash in Hand - Hundi
        else:
            debit_account_code = '1101'  # Default to cash counter

        # Determine credit account (donation income type)
        credit_account_code = None
        if donation.payment_mode.upper() in ['CASH', 'COUNTER']:
            credit_account_code = '4101'  # Donation - Cash
        elif donation.payment_mode.upper() in ['UPI', 'ONLINE', 'CARD', 'NETBANKING']:
            credit_account_code = '4102'  # Donation - Online/UPI
        elif 'HUNDI' in donation.payment_mode.upper():
            credit_account_code = '4103'  # Hundi Collection
        else:
            credit_account_code = '4101'  # Default to cash donation

        # Get accounts
        debit_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == debit_account_code
        ).first()

        credit_account = db.query(Account).filter(
            Account.temple_id == temple_id,
            Account.account_code == credit_account_code
        ).first()

        if not debit_account or not credit_account:
            print(f"Warning: Accounts not found for donation {donation.receipt_number}")
            return None

        # Create narration
        narration = f"Donation from {donation.devotee.name if donation.devotee else 'Anonymous'}"
        if donation.category:
            narration += f" - {donation.category.name}"

        # Create journal entry
        journal_entry = JournalEntry(
            temple_id=temple_id,
            entry_date=donation.donation_date,
            entry_number=None,  # Will be generated below
            narration=narration,
            reference_type='DONATION',
            reference_id=donation.id,
            reference_number=donation.receipt_number,
            status='POSTED',
            created_by=donation.created_by
        )
        db.add(journal_entry)
        db.flush()  # Get journal_entry.id

        # Generate entry number
        year = donation.donation_date.year
        last_entry = db.query(JournalEntry).filter(
            JournalEntry.temple_id == temple_id,
            JournalEntry.id < journal_entry.id
        ).order_by(JournalEntry.id.desc()).first()

        seq = 1
        if last_entry and last_entry.entry_number:
            try:
                seq = int(last_entry.entry_number.split('-')[-1]) + 1
            except:
                seq = journal_entry.id

        journal_entry.entry_number = f"JE-{year}-{str(seq).zfill(5)}"

        # Create journal lines
        # Debit: Payment Account (Cash/Bank increases)
        debit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=debit_account.id,
            debit_amount=donation.amount,
            credit_amount=0,
            description=f"Donation received via {donation.payment_mode}"
        )

        # Credit: Donation Income (Income increases)
        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=credit_account.id,
            debit_amount=0,
            credit_amount=donation.amount,
            description=f"Donation income - {donation.category.name if donation.category else 'General'}"
        )

        db.add(debit_line)
        db.add(credit_line)

        return journal_entry

    except Exception as e:
        print(f"Error posting donation to accounting: {str(e)}")
        return None


# Pydantic Schemas
class DonationBase(BaseModel):
    devotee_name: str
    devotee_phone: str
    amount: float
    category: str
    payment_mode: str = "Cash"
    address: Optional[str] = None  # Street address
    pincode: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"


class DonationCreate(DonationBase):
    notes: Optional[str] = None


class DonationResponse(BaseModel):
    id: int
    receipt_number: str
    amount: float
    payment_mode: str
    donation_date: date
    devotee: Optional[dict] = None
    category: Optional[dict] = None
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_donation(
    donation: DonationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new donation"""
    # Find or create devotee
    devotee = db.query(Devotee).filter(Devotee.phone == donation.devotee_phone).first()
    if not devotee:
        # Create devotee if doesn't exist
        devotee = Devotee(
            name=donation.devotee_name,
            full_name=donation.devotee_name,
            phone=donation.devotee_phone,
            address=donation.address,
            pincode=donation.pincode,
            city=donation.city,
            state=donation.state,
            country=donation.country or "India",
            temple_id=current_user.temple_id if current_user else None
        )
        db.add(devotee)
        db.flush()
    else:
        # Update devotee info if provided
        if donation.address and not devotee.address:
            devotee.address = donation.address
        if donation.pincode and not devotee.pincode:
            devotee.pincode = donation.pincode
        if donation.city and not devotee.city:
            devotee.city = donation.city
        if donation.state and not devotee.state:
            devotee.state = donation.state
        if donation.country and not devotee.country:
            devotee.country = donation.country
        if donation.devotee_name and devotee.name != donation.devotee_name:
            devotee.name = donation.devotee_name
            devotee.full_name = donation.devotee_name
        db.flush()
    
    # Find or create category
    category = db.query(DonationCategory).filter(
        DonationCategory.name == donation.category
    ).first()
    if not category:
        category = DonationCategory(
            name=donation.category,
            temple_id=current_user.temple_id if current_user else None
        )
        db.add(category)
        db.flush()
    
    # Generate receipt number
    year = datetime.now().year
    last_donation = db.query(Donation).filter(
        func.extract('year', Donation.donation_date) == year
    ).order_by(Donation.id.desc()).first()
    
    seq = 1
    if last_donation and last_donation.receipt_number:
        try:
            seq = int(last_donation.receipt_number.split('-')[-1]) + 1
        except:
            seq = 1
    
    receipt_number = f"TMP001-{year}-{str(seq).zfill(5)}"
    
    # Create donation
    db_donation = Donation(
        temple_id=current_user.temple_id if current_user else None,
        devotee_id=devotee.id,
        category_id=category.id,
        receipt_number=receipt_number,
        amount=donation.amount,
        payment_mode=donation.payment_mode,
        donation_date=date.today(),
        financial_year=f"{year}-{str(year+1)[-2:]}",
        notes=donation.notes,
        created_by=current_user.id if current_user else None
    )
    db.add(db_donation)
    db.commit()
    db.refresh(db_donation)

    # Post to accounting system
    journal_entry = post_donation_to_accounting(db, db_donation, current_user.temple_id if current_user else None)
    if journal_entry:
        db.commit()  # Commit the journal entry

    return {
        "id": db_donation.id,
        "receipt_number": db_donation.receipt_number,
        "amount": db_donation.amount,
        "journal_entry": journal_entry.entry_number if journal_entry else None,
        "message": "Donation recorded successfully and posted to accounting"
    }


@router.get("/", response_model=List[DonationResponse])
def get_donations(
    skip: int = 0,
    limit: int = 100,
    date: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of donations"""
    query = db.query(Donation)
    
    if date:
        query = query.filter(Donation.donation_date == date)
    elif date_from and date_to:
        query = query.filter(
            and_(
                Donation.donation_date >= date_from,
                Donation.donation_date <= date_to
            )
        )
    
    donations = query.order_by(Donation.donation_date.desc()).offset(skip).limit(limit).all()
    
    # Format response
    result = []
    for d in donations:
        result.append({
            "id": d.id,
            "receipt_number": d.receipt_number,
            "amount": d.amount,
            "payment_mode": d.payment_mode,
            "donation_date": d.donation_date,
            "devotee": {
                "id": d.devotee.id if d.devotee else None,
                "name": d.devotee.name if d.devotee else None,
                "phone": d.devotee.phone if d.devotee else None,
                "email": d.devotee.email if d.devotee else None,
                "address": d.devotee.address if d.devotee else None
            } if d.devotee else None,
            "devotee_phone": d.devotee.phone if d.devotee else None,  # For backward compatibility
            "category": {
                "id": d.category.id if d.category else None,
                "name": d.category.name if d.category else None
            } if d.category else None,
            "created_at": d.created_at
        })
    
    return result


@router.get("/report/daily")
def get_daily_report(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get daily donation report"""
    from datetime import date as date_class
    report_date = date if date else date_class.today().isoformat()
    
    donations = db.query(Donation).filter(
        Donation.donation_date == report_date
    ).all()
    
    total = sum(d.amount for d in donations)
    
    # Group by category
    by_category = {}
    for d in donations:
        cat_name = d.category.name if d.category else "Unknown"
        if cat_name not in by_category:
            by_category[cat_name] = {"amount": 0, "count": 0}
        by_category[cat_name]["amount"] += d.amount
        by_category[cat_name]["count"] += 1
    
    return {
        "date": report_date,
        "total": total,
        "count": len(donations),
        "by_category": [
            {"category": k, "amount": v["amount"], "count": v["count"]}
            for k, v in by_category.items()
        ]
    }


@router.get("/report/monthly")
def get_monthly_report(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly donation report"""
    donations = db.query(Donation).filter(
        func.extract('year', Donation.donation_date) == year,
        func.extract('month', Donation.donation_date) == month
    ).all()
    
    total = sum(d.amount for d in donations)
    
    # Group by category
    by_category = {}
    for d in donations:
        cat_name = d.category.name if d.category else "Unknown"
        if cat_name not in by_category:
            by_category[cat_name] = {"amount": 0, "count": 0}
        by_category[cat_name]["amount"] += d.amount
        by_category[cat_name]["count"] += 1
    
    return {
        "month": month,
        "year": year,
        "total": total,
        "count": len(donations),
        "by_category": [
            {"category": k, "amount": v["amount"], "count": v["count"]}
            for k, v in by_category.items()
        ]
    }


@router.get("/export/pdf")
def export_donations_pdf(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export donations to PDF format"""
    # Get temple info
    temple = None
    temple_logo_path = None
    if current_user and current_user.temple_id:
        temple = db.query(Temple).filter(Temple.id == current_user.temple_id).first()
        if temple and temple.logo_url:
            # Try to download logo if it's a URL, or use local path
            try:
                if temple.logo_url.startswith('http'):
                    # Download logo
                    response = requests.get(temple.logo_url, timeout=5)
                    if response.status_code == 200:
                        logo_data = io.BytesIO(response.content)
                        temple_logo_path = logo_data
                else:
                    # Local file path
                    if os.path.exists(temple.logo_url):
                        temple_logo_path = temple.logo_url
            except:
                temple_logo_path = None
    
    query = db.query(Donation)
    
    if date_from and date_to:
        query = query.filter(
            and_(
                Donation.donation_date >= date_from,
                Donation.donation_date <= date_to
            )
        )
    
    donations = query.order_by(Donation.donation_date.desc()).all()
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#FF9933'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    # Temple header
    if temple:
        if temple_logo_path:
            try:
                logo = Image(temple_logo_path, width=1*inch, height=1*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 0.1*inch))
            except:
                pass
        
        if temple.name:
            elements.append(Paragraph(temple.name, title_style))
        
        if temple.address:
            elements.append(Paragraph(temple.address, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        if temple.phone:
            elements.append(Paragraph(f"Phone: {temple.phone}", styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
    
    # Report title
    report_title = "DONATION REPORT"
    if date_from and date_to:
        report_title += f"<br/><font size=10>Period: {date_from} to {date_to}</font>"
    elements.append(Paragraph(report_title, title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Table data
    table_data = [["Receipt", "Date", "Devotee", "Phone", "Amount (₹)", "Category", "Payment"]]
    
    total_amount = 0
    for d in donations:
        table_data.append([
            d.receipt_number or "",
            d.donation_date.strftime('%d-%m-%Y') if d.donation_date else "",
            d.devotee.name if d.devotee else "",
            d.devotee.phone if d.devotee else "",
            f"{d.amount:,.0f}",
            d.category.name if d.category else "",
            d.payment_mode or ""
        ])
        total_amount += d.amount
    
    # Total row
    table_data.append([
        "TOTAL", "", "", "", f"<b>{total_amount:,.0f}</b>", f"{len(donations)} donations", ""
    ])
    
    # Create table
    table = Table(table_data, colWidths=[1.2*inch, 0.9*inch, 1.2*inch, 1*inch, 0.9*inch, 1.2*inch, 0.8*inch])
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9933')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # Total row
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_text = f"Generated on {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} | MandirSync Temple Management System"
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    filename = f"donations_{date_from or 'all'}_{date_to or date.today()}.pdf"
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/excel")
def export_donations_excel(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export donations to Excel format"""
    # Get temple info
    temple = None
    temple_logo_path = None
    if current_user and current_user.temple_id:
        temple = db.query(Temple).filter(Temple.id == current_user.temple_id).first()
        if temple and temple.logo_url:
            # Try to download logo if it's a URL, or use local path
            try:
                if temple.logo_url.startswith('http'):
                    # Download logo
                    response = requests.get(temple.logo_url, timeout=5)
                    if response.status_code == 200:
                        logo_data = io.BytesIO(response.content)
                        temple_logo_path = logo_data
                else:
                    # Local file path
                    if os.path.exists(temple.logo_url):
                        temple_logo_path = temple.logo_url
            except:
                temple_logo_path = None
    
    query = db.query(Donation)
    
    if date_from and date_to:
        query = query.filter(
            and_(
                Donation.donation_date >= date_from,
                Donation.donation_date <= date_to
            )
        )
    
    donations = query.order_by(Donation.donation_date.desc()).all()
    
    # Create Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Donations Report"
    
    # Styles
    header_fill = PatternFill(start_color="FF9933", end_color="FF9933", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    title_font = Font(bold=True, size=16, color="FF9933")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    row = 1
    
    # Temple header with logo
    if temple:
        # Add logo if available
        if temple_logo_path:
            try:
                logo = ExcelImage(temple_logo_path)
                logo.width = 100
                logo.height = 100
                ws.add_image(logo, 'A1')
                row = 4  # Start after logo
            except Exception as e:
                # Logo failed, continue without it
                row = 1
        
        ws.merge_cells(f'A{row}:G{row}')
        cell = ws.cell(row=row, column=1)
        cell.value = temple.name or "Temple Donations Report"
        cell.font = title_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        row += 1
        
        if temple.address:
            ws.merge_cells(f'A{row}:G{row}')
            cell = ws.cell(row=row, column=1)
            cell.value = temple.address
            cell.alignment = Alignment(horizontal='center', vertical='center')
            row += 1
        
        if temple.phone:
            ws.merge_cells(f'A{row}:G{row}')
            cell = ws.cell(row=row, column=1)
            cell.value = f"Phone: {temple.phone}"
            cell.alignment = Alignment(horizontal='center', vertical='center')
            row += 1
    
    # Report period
    if date_from and date_to:
        ws.merge_cells(f'A{row}:G{row}')
        cell = ws.cell(row=row, column=1)
        cell.value = f"Period: {date_from} to {date_to}"
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.font = Font(bold=True)
        row += 1
    
    row += 1  # Empty row
    
    # Headers
    headers = ["Receipt Number", "Date", "Devotee Name", "Phone", "Amount (₹)", "Category", "Payment Mode"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border
    
    row += 1
    
    # Data rows
    total_amount = 0
    for d in donations:
        ws.cell(row=row, column=1, value=d.receipt_number).border = border
        ws.cell(row=row, column=2, value=d.donation_date.strftime('%Y-%m-%d') if d.donation_date else "").border = border
        ws.cell(row=row, column=3, value=d.devotee.name if d.devotee else "").border = border
        ws.cell(row=row, column=4, value=d.devotee.phone if d.devotee else "").border = border
        ws.cell(row=row, column=5, value=d.amount).border = border
        ws.cell(row=row, column=6, value=d.category.name if d.category else "").border = border
        ws.cell(row=row, column=7, value=d.payment_mode).border = border
        total_amount += d.amount
        row += 1
    
    # Total row
    row += 1
    ws.merge_cells(f'A{row}:D{row}')
    cell = ws.cell(row=row, column=1)
    cell.value = "TOTAL"
    cell.font = Font(bold=True, size=12)
    cell.alignment = Alignment(horizontal='right', vertical='center')
    cell.border = border
    
    ws.cell(row=row, column=5, value=total_amount).font = Font(bold=True, size=12)
    ws.cell(row=row, column=5).border = border
    ws.cell(row=row, column=6, value=f"{len(donations)} donations").border = border
    ws.cell(row=row, column=7).border = border
    
    # Auto-adjust column widths
    for col in range(1, 8):
        ws.column_dimensions[get_column_letter(col)].width = 15
    
    # Save to BytesIO
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    filename = f"donations_{date_from or 'all'}_{date_to or date.today()}.xlsx"
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

