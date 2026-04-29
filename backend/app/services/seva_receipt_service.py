from datetime import datetime

from sqlalchemy.orm import Session

from app.models.seva import Seva, SevaBooking
from app.models.temple import Temple
from app.services.receipt_adapter_service import (
    build_base_receipt_payload,
    format_date,
    number_to_kannada_words,
    number_to_words,
    safe_text,
)
from app.services.receipt_template_service import build_compact_receipt_pdf


def _build_localized_copy(
    local_language: str,
    payment_mode: str,
    amount_words: str,
    amount_value: float,
) -> dict[str, str]:
    if local_language == "kannada":
        kannada_amount_words = number_to_kannada_words(int(round(amount_value or 0)))
        return {
            "receipt_title": "ಸೇವಾ ರಶೀದಿ / SEVA RECEIPT",
            "line_item_header": "ಸೇವಾ ವಿವರ / Seva Details",
            "service_date_label": "ಸೇವಾ ದಿನಾಂಕ / Seva Date",
            "amount_words_line": f"ರೂಪಾಯಿ {kannada_amount_words} ಮಾತ್ರ / Rupees {amount_words.upper()} ONLY",
            "payment_line": f"{payment_mode} ಮೂಲಕ ಕೆಳಗಿನ ಸೇವೆಗೆ ಕೃತಜ್ಞತೆಯಿಂದ ಸ್ವೀಕರಿಸಲಾಗಿದೆ. / Received with thanks for the below mentioned seva by {payment_mode}.",
            "note_local": "ಸೂಚನೆ: ಪೂಜೆ ಸಮಯಕ್ಕೆ 10 ನಿಮಿಷ ಮುಂಚೆ ಬಂದು ಪ್ರಸಾದವನ್ನು ಅದೇ ದಿನ ಸ್ವೀಕರಿಸಿ.",
        }

    return {
        "receipt_title": "SEVA RECEIPT",
        "line_item_header": "Seva Details",
        "service_date_label": "Seva Date",
        "amount_words_line": f"Received Rupees {amount_words.upper()} ONLY",
        "payment_line": f"Received with thanks for the below mentioned seva by {payment_mode}.",
        "note_local": "",
    }


def generate_seva_receipt_pdf(
    booking: SevaBooking,
    db: Session,
    temple_id: int = None,
    app_key: str = "mandirmitra",
):
    """Generate a compact Seva receipt PDF in A5 format using shared adapters."""
    temple = None

    if not temple_id:
        if booking.devotee and hasattr(booking.devotee, "temple_id"):
            temple_id = booking.devotee.temple_id
        elif booking.user and hasattr(booking.user, "temple_id"):
            temple_id = booking.user.temple_id

    if temple_id:
        temple = db.query(Temple).filter(Temple.id == temple_id).first()

    devotee = booking.devotee if hasattr(booking, "devotee") else None
    seva = booking.seva if hasattr(booking, "seva") else None
    if not seva and getattr(booking, "seva_id", None):
        seva = db.query(Seva).filter(Seva.id == booking.seva_id).first()

    amount_value = float(getattr(booking, "amount_paid", 0) or 0)
    amount_words = number_to_words(int(round(amount_value)))

    base_payload = build_base_receipt_payload(temple, app_key=app_key)
    local_language = safe_text(base_payload.get("local_language"), "").lower()
    receipt_number = safe_text(getattr(booking, "receipt_number", None), f"SEV{booking.id}")
    receipt_date = format_date(getattr(booking, "created_at", None) or datetime.utcnow())
    party_name = safe_text(
        devotee.name if devotee else getattr(booking, "devotee_names", None),
        "DEVOTEE",
    )
    address_value = safe_text(devotee.address if devotee else None, "--")
    seva_name_english = safe_text(getattr(seva, "name_english", None), "Seva Booking")
    seva_name_local = safe_text(getattr(seva, "name_kannada", None), "") if local_language == "kannada" else ""
    seva_name = f"{seva_name_local} / {seva_name_english}" if seva_name_local else seva_name_english
    payment_mode = safe_text(getattr(booking, "payment_method", None), "Cash")
    localized_copy = _build_localized_copy(local_language, payment_mode, amount_words, amount_value)

    payload = {
        **base_payload,
        "receipt_title": localized_copy["receipt_title"],
        "line_item_header": localized_copy["line_item_header"],
        "service_date_label": localized_copy["service_date_label"],
        "receipt_number": receipt_number,
        "receipt_date": receipt_date,
        "party_name": party_name,
        "address_value": address_value,
        "amount_words_line": localized_copy["amount_words_line"],
        "payment_line": localized_copy["payment_line"],
        "line_items": [{"description": seva_name, "amount": amount_value}],
        "total_amount": amount_value,
        "include_astro_row": True,
        "gotra": getattr(booking, "gotra", None),
        "nakshatra": getattr(booking, "nakshatra", None),
        "rashi": getattr(booking, "rashi", None),
        "service_date": format_date(getattr(booking, "booking_date", None)),
        "note_local": localized_copy["note_local"],
        "note_english": (
            "Note: Please be present 10 minutes before pooja time for Sankalpa and collect prasadam on the same day."
        ),
    }

    return build_compact_receipt_pdf(payload)
