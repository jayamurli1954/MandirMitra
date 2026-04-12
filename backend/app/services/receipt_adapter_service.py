import io
import os
from dataclasses import dataclass
from typing import Any

import requests

SUPPORTED_LOCAL_LANGUAGES = {"kannada", "tamil", "telugu", "malayalam", "hindi"}


@dataclass(frozen=True)
class ReceiptBranding:
    app_key: str
    app_display_name: str
    powered_by_line: str
    default_local_language: str = "kannada"
    temple_local_name_field: str = "name_kannada"


_BRANDING_REGISTRY = {
    "mandirmitra": ReceiptBranding(
        app_key="mandirmitra",
        app_display_name="MandirMitra",
        powered_by_line="Powered by MandirMitra.",
    ),
    "gruhamitra": ReceiptBranding(
        app_key="gruhamitra",
        app_display_name="GruhaMitra",
        powered_by_line="Powered by GruhaMitra.",
    ),
    "mitrabooks": ReceiptBranding(
        app_key="mitrabooks",
        app_display_name="MitraBooks",
        powered_by_line="Powered by MitraBooks.",
    ),
    "legalmitra": ReceiptBranding(
        app_key="legalmitra",
        app_display_name="LegalMitra",
        powered_by_line="Powered by LegalMitra.",
    ),
    "investmitra": ReceiptBranding(
        app_key="investmitra",
        app_display_name="InvestMitra",
        powered_by_line="Powered by InvestMitra.",
    ),
}


def get_receipt_branding(app_key: str | None = None) -> ReceiptBranding:
    key = str(app_key or "mandirmitra").strip().lower()
    return _BRANDING_REGISTRY.get(key, _BRANDING_REGISTRY["mandirmitra"])


def safe_text(value: Any, fallback: str = "--") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def format_date(value: Any) -> str:
    if not value:
        return "--"
    if hasattr(value, "strftime"):
        return value.strftime("%d/%m/%Y")
    text = str(value).strip()
    return text or "--"


def resolve_receipt_local_language(value: Any, default: str = "kannada") -> str:
    language = str(value or "").strip().lower()
    if language in SUPPORTED_LOCAL_LANGUAGES:
        return language
    return default


def load_media(source: str | None):
    if not source:
        return None

    try:
        if source.startswith("http"):
            response = requests.get(source, timeout=5)
            if response.status_code == 200 and response.content:
                return io.BytesIO(response.content)
            return None

        if os.path.exists(source):
            return source
    except Exception:
        return None

    return None


def number_to_words(n: int) -> str:
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

    def convert_hundreds(num: int) -> str:
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


def build_base_receipt_payload(
    temple: Any,
    app_key: str = "mandirmitra",
    local_language_override: str | None = None,
) -> dict:
    branding = get_receipt_branding(app_key)
    local_language = resolve_receipt_local_language(
        local_language_override or getattr(temple, "receipt_local_language", None),
        default=branding.default_local_language,
    )

    temple_local_line = safe_text(
        getattr(temple, branding.temple_local_name_field, None), fallback=""
    )
    header_local_line = temple_local_line or None
    if local_language != "kannada":
        header_local_line = None

    signature_source = load_media(getattr(temple, "signature_image_url", None))
    signatory_label = safe_text(getattr(temple, "authorized_signatory_designation", None), "")
    if not signatory_label:
        signatory_label = safe_text(
            getattr(temple, "authorized_signatory_name", None), "Authorized Signatory"
        )

    system_generated_line = ""
    if not signature_source:
        system_generated_line = "This is a system generated receipt and does not require any signature."

    return {
        "local_language": local_language,
        "header_local_line": header_local_line,
        "temple_name": getattr(temple, "name", None),
        "trust_name": getattr(temple, "trust_name", None),
        "address": getattr(temple, "address", None),
        "city": getattr(temple, "city", None),
        "state": getattr(temple, "state", None),
        "pincode": getattr(temple, "pincode", None),
        "website": getattr(temple, "website", None),
        "email": getattr(temple, "email", None),
        "phone": getattr(temple, "phone", None),
        "logo": load_media(getattr(temple, "logo_url", None)),
        "signature": signature_source,
        "signatory_label": signatory_label,
        "system_generated_line": system_generated_line,
        "powered_by_line": branding.powered_by_line,
    }
