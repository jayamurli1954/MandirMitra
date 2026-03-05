# Drik Panchanga Method Comparison (Review Only)

Date: 2026-02-28  
Purpose: Compare current MandirMitra Panchang calculation approach with `webresh/drik-panchanga` at formula/method level.  
Scope: Review only. No request to copy/replace implementation.

## Sources Reviewed

- Drik reference repository:
  - https://github.com/webresh/drik-panchanga
  - Core file mirror with readable line anchors:
    - https://cocalc.com/github/webresh/drik-panchanga/blob/master/panchanga.py
- MandirMitra code:
  - `backend/app/services/panchang/astro_utils.py`
  - `backend/app/services/panchang/celestial.py`
  - `backend/app/services/panchang/core.py`
  - `backend/app/services/panchang/timings.py`
  - `backend/app/services/panchang/calendrical.py`
  - `backend/app/services/panchang/__init__.py`

## Executive Summary

MandirMitra and Drik are aligned on core astronomical base (Swiss Ephemeris + sidereal/Lahiri style), but the calculation pipeline is **not identical**.  
The biggest practical divergence is in **Amrita Kalam / Varjyam handling**, where MandirMitra uses a custom Nakshatra-offset pipeline and day-window selection not present in the same way in Drik reference code.

## Formula-Level Mapping

| Topic | Drik (`panchanga.py`) | MandirMitra | Difference Impact |
|---|---|---|---|
| Julian day conversion | Uses local timezone offset in `gregorian_to_jd(...)` flow and place timezone object | `get_julian_day()` assumes IST directly (`-5.5` to UT) | Small offsets possible when non-IST or DST-sensitive contexts are introduced |
| Sidereal planet longitude | Swiss Ephemeris sidereal calculation | `get_sidereal_position()` with Lahiri (`swe.SIDM_LAHIRI`) | Broadly aligned |
| Sunrise/Sunset | `sunrise()`/`sunset()` via Swiss Ephemeris rise/set | `get_sun_rise_set_data()` via `swe.rise_trans` | Broadly aligned (minute-level numeric differences possible from flags/time conversions) |
| Moonrise/Moonset | `moonrise()`/`moonset()` via Swiss Ephemeris | `get_moon_rise_set_data()` via `swe.rise_trans` with date marker suffix | Broadly aligned |
| Tithi end-time | Computes tithi at sunrise + relative motion interpolation (`inverse_lagrange`) | Computes current elongation and finds transition with iterative `find_transition()` | Both valid; method differences can cause 1-5 minute drift near boundaries |
| Nakshatra end-time | Sunrise-anchor + interpolation using moon longitudes sampled at offsets | Absolute longitude boundary crossing with bracket + binary search (`_find_crossing`) | Usually close; can differ slightly around rapid longitude change |
| Yoga end-time | Sunrise-anchor interpolation on `(moon+sun)` | Transition search on `(moon+sun)` from query JD | Small minute-level differences expected |
| Karana | Uses tithi-based half-segmentation from sunrise state and interpolation | Uses elongation/6-degree indexing + transition search | Usually close; edge cases around Karana transition may differ |
| Rahu Kalam | Present (`rahu_kalam`) | Present (`get_rahu_kala_data`) | Operationally aligned |
| Yamaganda / Gulika | Drik has `yamaganda_kalam`; Gulika style handled via period definitions | Explicit `get_yamaganda_data`, `get_gulika_data` segment mapping | Segment tables can cause minute-level differences if convention differs |
| Dur Muhurta | Present (`durmuhurtam`) using weekday logic | `get_dur_muhurta_data` using `DUR_MUHURTA_INDICES` table | Manual index table choices can shift by several minutes |
| Abhijit | Present (`abhijit_muhurta`) | `get_abhijit_muhurat_data` | Aligned by formula style |
| Varjyam / Amrita | Not exposed in same direct form in inspected Drik file | `get_varjyam_impl_data()` using Nakshatra offset tables (`NAKSHATRA_VARJYAM_STARTS`, `NAKSHATRA_AMRITA_STARTS`) + event window selection | Main source of observed large mismatch |
| Hindu year labels (Shaka/Vikram/Samvatsara naming) | Not handled in same formatting layer in inspected Drik core file | Custom logic in `get_hindu_calendar_info_data()` | Naming/cycle output is implementation-specific, not direct Drik parity target |

## Specific Structural Differences in MandirMitra

1. Tithi/Nakshatra/Yoga/Karana are computed from current `jd` and transition search, not strictly sunrise-anchored interpolation.
2. Varjyam/Amrita are generated from static Nakshatra start-ghati tables and transformed to datetimes through Nakshatra span logic.
3. Day relevance selection uses explicit event filtering in `calculate_panchang()`:
   - `_get_neighbor_nakshatras(...)`
   - `_select_events_for_day_window(...)`
   - fallback to `_select_events_for_date(...)`
4. Hindu calendar display labels (Shaka/Vikram/Samvatsara strings) are from custom calendrical layer, not directly mirrored from Drik script output.

## Why You Can See 1-6 Minute Differences While Core Still Matches

- Different numerical method (interpolation vs transition search)
- Different anchor point (sunrise-based vs query-time-based)
- Step size and convergence strategy in root finding
- Time formatting and date-window inclusion rules

These are normal in independently implemented Panchang engines even when both rely on Swiss Ephemeris.

## Why Amrita/Varjyam Can Diverge More

- MandirMitra currently depends on:
  - hardcoded Nakshatra offset tables
  - Nakshatra start/end span derived from separate boundary search
  - additional event-window selection layer
- This stack is more sensitive to interpretation differences than core Tithi/Nakshatra itself.

## Final Assessment

- MandirMitra is **methodologically similar but not identical** to `webresh/drik-panchanga`.
- Core Panchang limbs are in the same family of astronomical computation.
- The largest non-parity area is **Amrita Kalam / Varjyam computation pipeline**, not Tithi/Nakshatra basics.

## Note

This document is a review artifact only and does not recommend changing frozen Panchang calculation code.

