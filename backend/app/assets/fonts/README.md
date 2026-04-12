Place local-language Unicode font files here for bilingual receipt rendering.

Supported secondary languages:
- Kannada
- Tamil
- Telugu
- Malayalam
- Hindi (Devanagari)

Bundled in this folder:
- NotoSansKannada-Variable.ttf (Google Fonts, OFL)
- OFL-NotoSansKannada.txt (license)

Optional additional files:
- NotoSansKannada-Regular.ttf
- NotoSansTamil-Regular.ttf
- NotoSansTelugu-Regular.ttf
- NotoSansMalayalam-Regular.ttf
- NotoSansDevanagari-Regular.ttf

The receipt engine checks this folder first, then `C:\Windows\Fonts`.
If no compatible local font is found, receipts fall back to English labels only.
