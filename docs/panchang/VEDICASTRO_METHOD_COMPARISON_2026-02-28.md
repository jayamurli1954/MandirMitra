# VedicAstro Method Comparison (Review Only)

Date: 2026-02-28  
Purpose: Compare MandirMitra Panchang calculation approach with `diliprk/VedicAstro` at method/scope level.  
Scope: Review only. No code-copy/fix recommendation.

## Sources Reviewed

- GitHub repository page and README content:
  - https://github.com/diliprk/VedicAstro
- PyPI package page (`vedicastro`) with same README/method summary:
  - https://pypi.org/project/vedicastro/

Note: In this environment, direct GitHub blob file content (`*.py`) was not retrievable due page rendering/access restrictions, so comparison is based on repository-declared methods and package documentation.

## Executive Summary

MandirMitra Panchang engine and `diliprk/VedicAstro` are **not the same calculation system**.

- MandirMitra: dedicated daily Panchang pipeline (Tithi, Nakshatra, Yoga, Karana, sunrise/sunset/moonrise/moonset, Rahu/Yamaganda/Gulika, Dur Muhurta, Amrita/Varjyam logic, Hindu calendar labels).
- VedicAstro: KP-focused horoscope/chart toolkit built around `flatlib` sidereal usage (chart generation, houses/planets tables, significators, Vimshottari Dasa, aspects, horary support).

## Feature/Method Mapping

| Area | VedicAstro (from repo/PyPI docs) | MandirMitra |
|---|---|---|
| Core focus | KP horoscope/charts | Daily Panchang + temple display |
| Primary class | `VedicHoroscopeData` | `PanchangService` |
| Core listed methods | `generate_chart`, `get_planets_data_from_chart`, `get_houses_data_from_chart`, `get_planet_wise_significators`, `get_house_wise_significators`, `compute_vimshottari_dasa`, `get_planetary_aspects` | `calculate_panchang`, plus modular methods for Tithi/Nakshatra/Yoga/Karana/timings |
| Dependency model | Uses `flatlib` sidereal branch + `pyswisseph` | Direct `pyswisseph` calls + custom transition/timing logic |
| Panchang-specific methods explicitly documented | Not listed as primary API in reviewed docs | Explicit and extensive |
| Horary (Prasna) | Explicitly documented | Not central in Panchang module |

## Calculation Architecture Difference (Important)

1. **Engine type mismatch**
   - VedicAstro is a horoscope computation toolkit (KP workflow).
   - MandirMitra is a Panchang calendar/timing engine for daily temple operations.

2. **Computation layer**
   - VedicAstro delegates a large part of chart math to `flatlib` sidereal.
   - MandirMitra implements its own Panchang transition logic in:
     - `astro_utils.py`
     - `core.py`
     - `timings.py`
     - `celestial.py`
     - `calendrical.py`

3. **Output goals**
   - VedicAstro outputs chart/significator/dasha/aspect-oriented data.
   - MandirMitra outputs daily Panchang consumable by temple UI (including devotional timing blocks).

## Practical Conclusion

- You are **not using the same calculation stack** as `diliprk/VedicAstro`.
- They share an astronomical ecosystem (sidereal + Swiss ephemeris family), but solve different problem domains with different method layers and outputs.
- Therefore, exact parity in Panchang timings should not be expected from this repository comparison.

## Reference Pointers in MandirMitra

- `backend/app/services/panchang/core.py`
- `backend/app/services/panchang/timings.py`
- `backend/app/services/panchang/astro_utils.py`
- `backend/app/services/panchang/celestial.py`
- `backend/app/services/panchang/calendrical.py`

