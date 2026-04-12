import io
import logging
import os
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

_BASE_DIR = os.path.dirname(__file__)
_FONTS_DIR = os.path.normpath(os.path.join(_BASE_DIR, '..', 'assets', 'fonts'))
_LOGGER = logging.getLogger(__name__)

_SCRIPT_RANGES = {
    'kannada': (0x0C80, 0x0CFF),
    'tamil': (0x0B80, 0x0BFF),
    'telugu': (0x0C00, 0x0C7F),
    'malayalam': (0x0D00, 0x0D7F),
    'hindi': (0x0900, 0x097F),
}

_SCRIPT_FONT_FILES = {
    'kannada': [
        'NotoSansKannada-Regular.ttf',
        'NotoSansKannada-Bold.ttf',
        'NotoSansKannada-Variable.ttf',
        'NotoSansKannada[wdth,wght].ttf',
        'Tunga.ttf',
        'Nirmala.ttc',
        'Nirmala.ttf',
    ],
    'tamil': ['NotoSansTamil-Regular.ttf', 'NotoSansTamil-Bold.ttf', 'Latha.ttf', 'Nirmala.ttc', 'Nirmala.ttf'],
    'telugu': ['NotoSansTelugu-Regular.ttf', 'NotoSansTelugu-Bold.ttf', 'Gautami.ttf', 'Nirmala.ttc', 'Nirmala.ttf'],
    'malayalam': ['NotoSansMalayalam-Regular.ttf', 'NotoSansMalayalam-Bold.ttf', 'Kartika.ttf', 'Nirmala.ttc', 'Nirmala.ttf'],
    'hindi': ['NotoSansDevanagari-Regular.ttf', 'NotoSansDevanagari-Bold.ttf', 'Mangal.ttf', 'Nirmala.ttc', 'Nirmala.ttf'],
}

_GENERIC_FONT_FILES = ['Nirmala.ttc', 'Nirmala.ttf', 'NirmalaB.ttf']

_SUPPORTED_LOCAL_LANGUAGES = {'kannada', 'tamil', 'telugu', 'malayalam', 'hindi'}

_LOCAL_LABELS = {
    'kannada': {
        'receipt_title': 'ರಶೀದಿ',
        'receipt_number': 'ರಸೀದಿ ಸಂಖ್ಯೆ',
        'date': 'ದಿನಾಂಕ',
        'party': 'ಶ್ರೀ/ಶ್ರೀಮತಿ',
        'address': 'ವಿಳಾಸ',
        'line_item': 'ಸೇವೆ ವಿವರ',
        'total': 'ಒಟ್ಟು',
        'gotra': 'ಗೋತ್ರ',
        'nakshatra': 'ನಕ್ಷತ್ರ',
        'rashi': 'ರಾಶಿ',
        'service_date': 'ಸೇವೆ ದಿನಾಂಕ',
        'cashier': 'ಖಜಾಂಚಿ',
        'note': 'ಸೂಚನೆ: ಪೂಜೆ ಸಮಯಕ್ಕೆ 10 ನಿಮಿಷ ಮುಂಚೆ ಆಗಮಿಸಿ ಮತ್ತು ಪ್ರಸಾದವನ್ನು ಅದೇ ದಿನ ಪಡೆಯಿರಿ.',
    },
    'tamil': {
        'receipt_title': 'ரசீது',
        'receipt_number': 'ரசீது எண்',
        'date': 'தேதி',
        'party': 'திரு/திருமதி',
        'address': 'முகவரி',
        'line_item': 'சேவை விவரம்',
        'total': 'மொத்தம்',
        'gotra': 'கோத்திரம்',
        'nakshatra': 'நட்சத்திரம்',
        'rashi': 'ராசி',
        'service_date': 'சேவை தேதி',
        'cashier': 'பொருளாளர்',
        'note': 'குறிப்பு: பூஜை நேரத்திற்கு 10 நிமிடம் முன்பு வரவும் மற்றும் அதே நாளில் பிரசாதம் பெறவும்.',
    },
    'telugu': {
        'receipt_title': 'రసీదు',
        'receipt_number': 'రసీదు సంఖ్య',
        'date': 'తేదీ',
        'party': 'శ్రీ/శ్రీమతి',
        'address': 'చిరునామా',
        'line_item': 'సేవ వివరాలు',
        'total': 'మొత్తం',
        'gotra': 'గోత్రం',
        'nakshatra': 'నక్షత్రం',
        'rashi': 'రాశి',
        'service_date': 'సేవ తేదీ',
        'cashier': 'ఖజాంచి',
        'note': 'గమనిక: పూజ సమయానికి 10 నిమిషాల ముందు రండి మరియు ప్రసాదం అదే రోజున తీసుకోండి.',
    },
    'malayalam': {
        'receipt_title': 'രസീത്',
        'receipt_number': 'രസീത് നമ്പർ',
        'date': 'തീയതി',
        'party': 'ശ്രീ/ശ്രീമതി',
        'address': 'വിലാസം',
        'line_item': 'സേവ വിശദാംശങ്ങൾ',
        'total': 'ആകെ',
        'gotra': 'ഗോത്രം',
        'nakshatra': 'നക്ഷത്രം',
        'rashi': 'രാശി',
        'service_date': 'സേവ തീയതി',
        'cashier': 'കാഷിയർ',
        'note': 'കുറിപ്പ്: പൂജ സമയം മുമ്പായി 10 മിനിറ്റ് നേരത്തെ എത്തി പ്രസാദം അതേ ദിവസം കൈപ്പറ്റുക.',
    },
    'hindi': {
        'receipt_title': 'रसीद',
        'receipt_number': 'रसीद संख्या',
        'date': 'दिनांक',
        'party': 'श्री/श्रीमती',
        'address': 'पता',
        'line_item': 'सेवा विवरण',
        'total': 'कुल',
        'gotra': 'गोत्र',
        'nakshatra': 'नक्षत्र',
        'rashi': 'राशि',
        'service_date': 'सेवा तिथि',
        'cashier': 'कैशियर',
        'note': 'नोट: कृपया पूजा समय से 10 मिनट पहले आएं और प्रसाद उसी दिन प्राप्त करें।',
    },
}

_ENGLISH_LABELS = {
    'receipt_title': 'RECEIPT',
    'receipt_number': 'Receipt No',
    'date': 'Date',
    'party': 'Smt/Sri',
    'address': 'Address',
    'line_item': 'Seva Details',
    'total': 'Total',
    'gotra': 'Gotra',
    'nakshatra': 'Star',
    'rashi': 'Rashi',
    'service_date': 'Seva Date',
    'cashier': 'Cashier',
}


def _normalize_local_language(value: Any) -> str | None:
    if value is None:
        return None
    language = str(value).strip().lower()
    return language if language in _SUPPORTED_LOCAL_LANGUAGES else None


def _detect_script(text: str) -> str | None:
    for char in text:
        code = ord(char)
        for script_name, (start, end) in _SCRIPT_RANGES.items():
            if start <= code <= end:
                return script_name
    return None


def _script_hint_from_payload(payload: dict) -> str | None:
    explicit_language = _normalize_local_language(payload.get('local_language'))
    if explicit_language:
        return explicit_language

    script_hint = _detect_script(str(payload.get('header_local_line') or ''))
    if script_hint:
        return script_hint

    script_hint = _detect_script(str(payload.get('receipt_title') or ''))
    if script_hint:
        return script_hint

    script_hint = _detect_script(str(payload.get('note_local') or ''))
    if script_hint:
        return script_hint

    return None


def _font_candidate_paths(script_hint: str | None) -> list[str]:
    candidates: list[str] = []

    env_font_file = os.getenv('RECEIPT_FONT_FILE', '').strip()
    if env_font_file:
        candidates.append(env_font_file)

    script_files = _SCRIPT_FONT_FILES.get(script_hint or '', [])
    for file_name in script_files:
        candidates.append(os.path.join(_FONTS_DIR, file_name))
        candidates.append(os.path.join(r'C:\Windows\Fonts', file_name))

    for file_name in _GENERIC_FONT_FILES:
        candidates.append(os.path.join(_FONTS_DIR, file_name))
        candidates.append(os.path.join(r'C:\Windows\Fonts', file_name))

    seen = set()
    deduped = []
    for path in candidates:
        normalized = os.path.normpath(path)
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)

    return deduped


def _resolve_font_name(script_hint: str | None) -> str:
    for idx, path in enumerate(_font_candidate_paths(script_hint)):
        if not os.path.exists(path):
            continue

        font_name = f'MandirReceipt_{script_hint or "generic"}_{idx}'
        if font_name not in pdfmetrics.getRegisteredFontNames():
            try:
                pdfmetrics.registerFont(TTFont(font_name, path))
            except Exception:
                continue
        return font_name

    return 'Helvetica'


def _as_text(value: Any, fallback: str = '') -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _split_amount(value: Any) -> tuple[str, str]:
    try:
        amount = float(value or 0)
    except Exception:
        amount = 0.0

    normalized = f'{amount:.2f}'
    major, minor = normalized.split('.', 1)
    return major, minor


def _paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(_as_text(text, '-')).replace('\n', '<br/>'), style)


def _bilingual_label(local_label: str, english_label: str, use_local_labels: bool) -> str:
    if use_local_labels and local_label:
        return f'{local_label} / {english_label}'
    return english_label


def _default_labels(local_language: str | None, use_local_labels: bool) -> dict[str, str]:
    local_labels = _LOCAL_LABELS.get(local_language or '', {})
    return {
        'receipt_title': _bilingual_label(local_labels.get('receipt_title', ''), _ENGLISH_LABELS['receipt_title'], use_local_labels),
        'receipt_number': _bilingual_label(local_labels.get('receipt_number', ''), _ENGLISH_LABELS['receipt_number'], use_local_labels),
        'date': _bilingual_label(local_labels.get('date', ''), _ENGLISH_LABELS['date'], use_local_labels),
        'party': _bilingual_label(local_labels.get('party', ''), _ENGLISH_LABELS['party'], use_local_labels),
        'address': _bilingual_label(local_labels.get('address', ''), _ENGLISH_LABELS['address'], use_local_labels),
        'line_item': _bilingual_label(local_labels.get('line_item', ''), _ENGLISH_LABELS['line_item'], use_local_labels),
        'total': _bilingual_label(local_labels.get('total', ''), _ENGLISH_LABELS['total'], use_local_labels),
        'gotra': _bilingual_label(local_labels.get('gotra', ''), _ENGLISH_LABELS['gotra'], use_local_labels),
        'nakshatra': _bilingual_label(local_labels.get('nakshatra', ''), _ENGLISH_LABELS['nakshatra'], use_local_labels),
        'rashi': _bilingual_label(local_labels.get('rashi', ''), _ENGLISH_LABELS['rashi'], use_local_labels),
        'service_date': _bilingual_label(local_labels.get('service_date', ''), _ENGLISH_LABELS['service_date'], use_local_labels),
        'cashier': _bilingual_label(local_labels.get('cashier', ''), _ENGLISH_LABELS['cashier'], use_local_labels),
        'note_local': local_labels.get('note', ''),
    }


def _resolve_label(payload_value: Any, labels: dict[str, str], key: str, local_language: str | None, use_local_labels: bool) -> str:
    provided = _as_text(payload_value, '')
    if not provided:
        return labels[key]

    if not use_local_labels:
        return provided

    local_label = _LOCAL_LABELS.get(local_language or '', {}).get(key, '')
    if not local_label or local_label in provided:
        return provided

    return f'{local_label} / {provided}'


def build_compact_receipt_pdf(payload: dict) -> io.BytesIO:
    script_hint = _script_hint_from_payload(payload)
    font_name = _resolve_font_name(script_hint)
    has_local_font = font_name != 'Helvetica'

    local_language = _normalize_local_language(payload.get('local_language')) or script_hint
    if local_language in _SUPPORTED_LOCAL_LANGUAGES and not has_local_font:
        _LOGGER.warning(
            "Local receipt language '%s' selected but no compatible local-script font was found. Falling back to English labels.",
            local_language,
        )

    use_local_labels = bool(payload.get('use_local_labels', has_local_font and local_language in _SUPPORTED_LOCAL_LANGUAGES))
    labels = _default_labels(local_language, use_local_labels)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A5,
        leftMargin=8 * mm,
        rightMargin=8 * mm,
        topMargin=8 * mm,
        bottomMargin=8 * mm,
    )

    styles = getSampleStyleSheet()
    header_title = ParagraphStyle(
        'ReceiptHeaderTitle',
        parent=styles['Heading3'],
        fontName=font_name,
        fontSize=12,
        leading=14,
        alignment=1,
        spaceAfter=2,
    )
    header_line = ParagraphStyle(
        'ReceiptHeaderLine',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=8.5,
        leading=10,
        alignment=1,
    )
    table_cell = ParagraphStyle(
        'ReceiptTableCell',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=12,
    )
    table_cell_center = ParagraphStyle(
        'ReceiptTableCellCenter',
        parent=table_cell,
        alignment=1,
    )
    table_cell_right = ParagraphStyle(
        'ReceiptTableCellRight',
        parent=table_cell,
        alignment=2,
    )
    footer_note = ParagraphStyle(
        'ReceiptFooterNote',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        leading=11,
        alignment=1,
    )

    elements: list[Any] = []

    logo_obj = None
    logo_source = payload.get('logo')
    if logo_source:
        try:
            logo_obj = Image(logo_source, width=16 * mm, height=16 * mm)
        except Exception:
            logo_obj = None

    trust_name = _as_text(payload.get('trust_name'))
    temple_name = _as_text(payload.get('temple_name'))
    primary_header = trust_name or temple_name or 'Temple Trust'
    secondary_header = temple_name if trust_name and temple_name and temple_name != trust_name else ''

    header_lines = []
    header_local_line = _as_text(payload.get('header_local_line'))
    if header_local_line and use_local_labels:
        header_lines.append(_paragraph(header_local_line, header_line))
    header_lines.append(_paragraph(primary_header, header_title))

    if secondary_header:
        header_lines.append(_paragraph(secondary_header, header_line))

    address = _as_text(payload.get('address'))
    city = _as_text(payload.get('city'))
    state = _as_text(payload.get('state'))
    pincode = _as_text(payload.get('pincode'))
    address_line = ' '.join(part for part in [address, city, state, pincode] if part)
    if address_line:
        header_lines.append(_paragraph(address_line, header_line))

    website = _as_text(payload.get('website'))
    email = _as_text(payload.get('email'))
    phone = _as_text(payload.get('phone'))
    if website:
        header_lines.append(_paragraph(website, header_line))
    if email:
        header_lines.append(_paragraph(email, header_line))
    if phone:
        header_lines.append(_paragraph(f'Phone : {phone}', header_line))

    if logo_obj:
        logo_width = 22 * mm
        header_table = Table([[logo_obj, header_lines]], colWidths=[logo_width, doc.width - logo_width])
        header_table.setStyle(
            TableStyle(
                [
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 1),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ]
            )
        )
        elements.append(header_table)
    else:
        elements.extend(header_lines)

    elements.append(Spacer(1, 4))

    line_items = payload.get('line_items') or []
    if not line_items:
        line_items = [{'description': '-', 'amount': payload.get('total_amount', 0)}]

    total_amount = payload.get('total_amount')
    if total_amount is None and line_items:
        try:
            total_amount = sum(float(item.get('amount') or 0) for item in line_items)
        except Exception:
            total_amount = 0

    receipt_title = _resolve_label(payload.get('receipt_title'), labels, 'receipt_title', local_language, use_local_labels)
    receipt_no_label = _resolve_label(payload.get('receipt_number_label'), labels, 'receipt_number', local_language, use_local_labels)
    date_label = _resolve_label(payload.get('date_label'), labels, 'date', local_language, use_local_labels)
    party_label = _resolve_label(payload.get('party_label'), labels, 'party', local_language, use_local_labels)
    address_label = _resolve_label(payload.get('address_label'), labels, 'address', local_language, use_local_labels)
    line_item_header = _resolve_label(payload.get('line_item_header'), labels, 'line_item', local_language, use_local_labels)
    total_label = _resolve_label(payload.get('total_label'), labels, 'total', local_language, use_local_labels)
    gotra_label = _resolve_label(payload.get('gotra_label'), labels, 'gotra', local_language, use_local_labels)
    star_label = _resolve_label(payload.get('nakshatra_label'), labels, 'nakshatra', local_language, use_local_labels)
    rashi_label = _resolve_label(payload.get('rashi_label'), labels, 'rashi', local_language, use_local_labels)
    service_date_label = _resolve_label(payload.get('service_date_label'), labels, 'service_date', local_language, use_local_labels)
    cashier_label = _resolve_label(payload.get('cashier_label'), labels, 'cashier', local_language, use_local_labels)
    signatory_label = _as_text(payload.get('signatory_label'), cashier_label)

    signature_cell: Any = _paragraph(signatory_label, table_cell_center)
    signature_source = payload.get('signature')
    if signature_source:
        try:
            signature_image = Image(signature_source, width=28 * mm, height=10 * mm)
            signature_cell = [signature_image, Spacer(1, 1), _paragraph(signatory_label, table_cell_center)]
        except Exception:
            signature_cell = _paragraph(signatory_label, table_cell_center)

    rows: list[list[Any]] = []
    rows.append([_paragraph(receipt_title, table_cell_center), '', ''])
    rows.append([
        _paragraph(f'{receipt_no_label}: {_as_text(payload.get("receipt_number"), "-")}', table_cell),
        _paragraph(date_label, table_cell_center),
        _paragraph(_as_text(payload.get('receipt_date'), '-'), table_cell_center),
    ])
    rows.append([
        _paragraph(
            f'{party_label} {_as_text(payload.get("party_name"), "-")}',
            table_cell,
        ),
        '',
        '',
    ])
    rows.append([
        _paragraph(f'{address_label} {_as_text(payload.get("address_value"), "--")}', table_cell),
        '',
        '',
    ])
    rows.append([
        _paragraph(
            _as_text(payload.get('amount_words_line'), 'Received with thanks'),
            table_cell,
        ),
        '',
        '',
    ])
    rows.append([
        _paragraph(
            _as_text(payload.get('payment_line'), 'Received with thanks.'),
            table_cell,
        ),
        '',
        '',
    ])

    rows.append([
        _paragraph(line_item_header, table_cell_center),
        _paragraph('Rs', table_cell_center),
        _paragraph('-', table_cell_center),
    ])

    for item in line_items:
        major, minor = _split_amount(item.get('amount'))
        rows.append([
            _paragraph(_as_text(item.get('description'), '-'), table_cell),
            _paragraph(major, table_cell_right),
            _paragraph(minor, table_cell_right),
        ])

    total_major, total_minor = _split_amount(total_amount)
    rows.append([
        _paragraph(total_label, table_cell_right),
        _paragraph(total_major, table_cell_right),
        _paragraph(total_minor, table_cell_right),
    ])

    if payload.get('include_astro_row', True):
        rows.append([
            _paragraph(f'{gotra_label} {_as_text(payload.get("gotra"), "--")}', table_cell),
            _paragraph(f'{star_label} {_as_text(payload.get("nakshatra"), "--")}', table_cell),
            _paragraph(f'{rashi_label} {_as_text(payload.get("rashi"), "--")}', table_cell),
        ])

    rows.append([
        _paragraph(
            f'{service_date_label} {_as_text(payload.get("service_date"), "--")}',
            table_cell,
        ),
        _paragraph('', table_cell_center),
        signature_cell,
    ])

    note_line_local = _as_text(payload.get('note_local'), labels['note_local'])
    note_line_english = _as_text(payload.get('note_english'), '')
    note_lines = [line for line in [note_line_local if use_local_labels else '', note_line_english] if line]
    note_block = '<br/>'.join(note_lines)
    rows.append([_paragraph(note_block or '-', table_cell_center), '', ''])

    col1 = doc.width * 0.72
    col2 = doc.width * 0.18
    col3 = doc.width - col1 - col2
    table = Table(rows, colWidths=[col1, col2, col3])

    item_start_index = 7
    item_end_index = item_start_index + len(line_items) - 1
    note_row_index = len(rows) - 1

    table_style = [
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#808080')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#A0A0A0')),
        ('SPAN', (0, 0), (2, 0)),
        ('SPAN', (0, 2), (2, 2)),
        ('SPAN', (0, 3), (2, 3)),
        ('SPAN', (0, 4), (2, 4)),
        ('SPAN', (0, 5), (2, 5)),
        ('SPAN', (0, note_row_index), (2, note_row_index)),
        ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#F2F2F2')),
        ('BACKGROUND', (0, 6), (2, 6), colors.HexColor('#F8F8F8')),
        ('BACKGROUND', (0, note_row_index), (2, note_row_index), colors.HexColor('#F8F8F8')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]

    if item_end_index >= item_start_index:
        table_style.append(('ALIGN', (1, item_start_index), (2, item_end_index), 'RIGHT'))

    table.setStyle(TableStyle(table_style))
    elements.append(table)
    elements.append(Spacer(1, 6))

    system_line_raw = payload.get('system_generated_line')
    if system_line_raw is None:
        system_line = 'This is a system generated receipt and does not require any signature.'
    else:
        system_line = str(system_line_raw).strip()

    powered_by = _as_text(payload.get('powered_by_line'), 'Powered by MandirMitra.')

    if system_line:
        elements.append(_paragraph(system_line, footer_note))
        elements.append(Spacer(1, 2))
    elements.append(_paragraph(powered_by, footer_note))

    doc.build(elements)
    buffer.seek(0)
    return buffer

