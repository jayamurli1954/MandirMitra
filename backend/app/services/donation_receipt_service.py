from datetime import datetime

from sqlalchemy.orm import Session

from app.models.donation import Donation, DonationType
from app.models.temple import Temple
from app.services.receipt_adapter_service import (
    build_base_receipt_payload,
    format_date,
    number_to_kannada_words,
    number_to_words,
    safe_text,
)
from app.services.receipt_template_service import build_compact_receipt_pdf


def _is_in_kind_donation(donation_type_value) -> bool:
    if isinstance(donation_type_value, DonationType):
        return donation_type_value == DonationType.IN_KIND
    if isinstance(donation_type_value, str):
        return donation_type_value.strip().lower() == DonationType.IN_KIND.value
    return str(donation_type_value).strip().lower() == DonationType.IN_KIND.value


def _build_line_items(donation: Donation, category_name: str, is_in_kind: bool) -> list[dict]:
    amount_value = float(getattr(donation, "amount", 0) or 0)

    if not is_in_kind:
        payment_mode = safe_text(getattr(donation, "payment_mode", None), "Cash")
        description = safe_text(category_name, "Donation")
        return [{"description": f"{description} ({payment_mode})", "amount": amount_value}]

    item_name = safe_text(getattr(donation, "item_name", None), "In-Kind Donation")
    description_lines = [item_name]

    item_description = safe_text(getattr(donation, "item_description", None), "")
    if item_description:
        description_lines.append(item_description)

    quantity = getattr(donation, "quantity", None)
    unit = safe_text(getattr(donation, "unit", None), "")
    if quantity and unit:
        description_lines.append(f"Quantity: {quantity} {unit}")
    elif quantity:
        description_lines.append(f"Quantity: {quantity}")

    purity = safe_text(getattr(donation, "purity", None), "")
    if purity:
        description_lines.append(f"Purity: {purity}")

    weight_gross = getattr(donation, "weight_gross", None)
    if weight_gross:
        description_lines.append(f"Gross Weight: {weight_gross} g")

    weight_net = getattr(donation, "weight_net", None)
    if weight_net:
        description_lines.append(f"Net Weight: {weight_net} g")

    return [{"description": "\n".join(description_lines), "amount": amount_value}]


def _build_donation_note(temple, category) -> str:
    if category and getattr(category, "is_80g_eligible", False):
        certificate_number = safe_text(getattr(temple, "certificate_80g_number", None), "")
        valid_to = safe_text(getattr(temple, "certificate_80g_valid_to", None), "")
        if certificate_number and valid_to:
            return f"Donation eligible under 80G. Certificate No: {certificate_number} (Valid up to {valid_to})."
        if certificate_number:
            return f"Donation eligible under 80G. Certificate No: {certificate_number}."
        return "Donation eligible under 80G as per trust compliance records."
    return "Thank you for your generous contribution."


def _build_localized_copy(
    local_language: str,
    is_in_kind: bool,
    payment_mode: str,
    amount_words: str,
    amount_value: float,
) -> dict[str, str]:
    if local_language == "kannada":
        kannada_amount_words = number_to_kannada_words(int(round(amount_value or 0)))
        if is_in_kind:
            return {
                "receipt_title": "ದೇಣಿಗೆ ರಶೀದಿ / DONATION RECEIPT",
                "line_item_header": "ದೇಣಿಗೆ ವಿವರ / Donation Details",
                "service_date_label": "ದೇಣಿಗೆ ದಿನಾಂಕ / Donation Date",
                "amount_words_line": f"ಸ್ವೀಕರಿಸಿದ ಮೌಲ್ಯ ರೂಪಾಯಿ {kannada_amount_words} ಮಾತ್ರ / Received Assessed Value Rupees {amount_words.upper()} ONLY",
                "payment_line": "ವಸ್ತುರೂಪದ ದೇಣಿಗೆಯನ್ನು ಕೃತಜ್ಞತೆಯಿಂದ ಸ್ವೀಕರಿಸಲಾಗಿದೆ. / Received with thanks towards in-kind donation.",
                "note_local": "ನಿಮ್ಮ ದೇಣಿಗೆಗೆ ಹೃತ್ಪೂರ್ವಕ ಧನ್ಯವಾದಗಳು.",
            }

        return {
            "receipt_title": "ದೇಣಿಗೆ ರಶೀದಿ / DONATION RECEIPT",
            "line_item_header": "ದೇಣಿಗೆ ವಿವರ / Donation Details",
            "service_date_label": "ದೇಣಿಗೆ ದಿನಾಂಕ / Donation Date",
            "amount_words_line": f"ರೂಪಾಯಿ {kannada_amount_words} ಮಾತ್ರ / Rupees {amount_words.upper()} ONLY",
            "payment_line": f"{payment_mode} ಮೂಲಕ ನೀಡಿದ ದೇಣಿಗೆಯನ್ನು ಕೃತಜ್ಞತೆಯಿಂದ ಸ್ವೀಕರಿಸಲಾಗಿದೆ. / Received with thanks towards donation by {payment_mode}.",
            "note_local": "ನಿಮ್ಮ ದೇಣಿಗೆಗೆ ಹೃತ್ಪೂರ್ವಕ ಧನ್ಯವಾದಗಳು.",
        }

    payment_line = "Received with thanks towards in-kind donation."
    amount_words_prefix = "Received Assessed Value Rupees"
    if not is_in_kind:
        payment_line = f"Received with thanks towards donation by {payment_mode}."
        amount_words_prefix = "Received Rupees"

    return {
        "receipt_title": "DONATION RECEIPT",
        "line_item_header": "Donation Details",
        "service_date_label": "Donation Date",
        "amount_words_line": f"{amount_words_prefix} {amount_words.upper()} ONLY",
        "payment_line": payment_line,
        "note_local": "",
    }


def generate_receipt_pdf(
    donation: Donation,
    db: Session,
    app_key: str = "mandirmitra",
):
    """Generate a compact donation receipt PDF in A5 format using shared adapters."""
    temple = None
    if getattr(donation, "temple_id", None):
        temple = db.query(Temple).filter(Temple.id == donation.temple_id).first()

    devotee = donation.devotee if hasattr(donation, "devotee") else None
    category = donation.category if hasattr(donation, "category") else None

    is_in_kind = _is_in_kind_donation(getattr(donation, "donation_type", None))
    amount_value = float(getattr(donation, "amount", 0) or 0)
    amount_words = number_to_words(int(round(amount_value)))

    base_payload = build_base_receipt_payload(temple, app_key=app_key)
    payment_mode = safe_text(getattr(donation, "payment_mode", None), "Cash")
    category_name = safe_text(getattr(category, "name", None), "Donation")
    local_language = safe_text(base_payload.get("local_language"), "").lower()
    localized_copy = _build_localized_copy(
        local_language,
        is_in_kind,
        payment_mode,
        amount_words,
        amount_value,
    )

    payload = {
        **base_payload,
        "receipt_title": localized_copy["receipt_title"],
        "line_item_header": localized_copy["line_item_header"],
        "service_date_label": localized_copy["service_date_label"],
        "receipt_number": safe_text(getattr(donation, "receipt_number", None), f"DON{donation.id}"),
        "receipt_date": format_date(getattr(donation, "donation_date", None) or datetime.utcnow()),
        "party_name": safe_text(devotee.name if devotee else None, "Anonymous Donor"),
        "address_value": safe_text(devotee.address if devotee else None, "--"),
        "amount_words_line": localized_copy["amount_words_line"],
        "payment_line": localized_copy["payment_line"],
        "line_items": _build_line_items(donation, category_name, is_in_kind),
        "total_amount": amount_value,
        "include_astro_row": False,
        "include_service_date_row": False,
        "service_date": format_date(getattr(donation, "donation_date", None)),
        "note_local": localized_copy["note_local"],
        "note_english": _build_donation_note(temple, category),
    }

    return build_compact_receipt_pdf(payload)
