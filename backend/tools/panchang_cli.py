"""
Simple internal Panchang CLI for calibration and testing.

Usage examples (from backend venv):

  python -m tools.panchang_cli --date 2025-12-01 --lat 12.9716 --lon 77.5946

This does NOT call any external services. It uses the same PanchangService
and Swiss Ephemeris + Lahiri ayanamsa that the API uses and prints a compact
text report so you can compare it manually with Drik Panchang / Rashtriya
Panchang while refining the algorithms.
"""

from __future__ import annotations

import argparse
from datetime import datetime

from app.services.panchang_service import PanchangService


def format_field(label: str, value: str | None) -> str:
    return f"{label:<18}: {value if value is not None else 'N/A'}"


def run(date_str: str, lat: float, lon: float, city: str) -> None:
    """
    Run panchang calculation for a single date and print key fields.
    """
    # Parse date with no time component; service will use current time of that date
    dt = datetime.strptime(date_str, "%Y-%m-%d")

    service = PanchangService()
    data = service.calculate_panchang(dt, lat, lon, city)

    # Basic date info
    gregorian = data["date"]["gregorian"]
    hindu = data["date"]["hindu"]

    print("=== Panchang Calibration Output ===")
    print(f"Date           : {gregorian['date']} ({gregorian['formatted']})")
    print(f"Location       : {city} (lat={lat}, lon={lon})")
    print()

    # Sun & Moon timings
    sun_moon = data.get("sun_moon", {})
    print("Sun & Moon")
    print(format_field("Sunrise", sun_moon.get("sunrise")))
    print(format_field("Sunset", sun_moon.get("sunset")))
    print(format_field("Moonrise", sun_moon.get("moonrise")))
    print(format_field("Moonset", sun_moon.get("moonset")))
    print()

    # Core panchang
    panchang = data.get("panchang", {})
    tithi = panchang.get("tithi", {})
    nak = panchang.get("nakshatra", {})
    yoga = panchang.get("yoga", {})
    karana = panchang.get("karana", {})

    print("Core Panchang")
    print(format_field("Tithi", tithi.get("name")))
    print(format_field("Tithi ends", tithi.get("end_time")))
    print(format_field("Nakshatra", nak.get("name")))
    print(format_field("Nakshatra ends", nak.get("end_time")))
    print(format_field("Yoga", yoga.get("name")))
    print(format_field("Yoga ends", yoga.get("end_time")))
    print(format_field("Karana", karana.get("name")))
    print(format_field("Paksha", tithi.get("paksha")))
    print()

    # Hindu calendar info
    print("Hindu Calendar")
    print(format_field("Vikram Samvat", str(hindu.get("vikram_samvat"))))
    print(format_field("Shaka Samvat", str(hindu.get("shaka_samvat"))))
    print(format_field("Lunar month (P)", hindu.get("lunar_month_purnimanta")))
    print(format_field("Lunar month (A)", hindu.get("lunar_month_amanta")))
    print(format_field("Paksha", hindu.get("paksha")))
    print(format_field("Ritu", hindu.get("ritu")))
    print()

    # Inauspicious times
    ina = data.get("inauspicious_times", {})
    rahu = ina.get("rahu_kaal", {})
    yama = ina.get("yamaganda", {})
    gulika = ina.get("gulika", {})

    def fmt_period(p: dict | None) -> str:
        if not p:
            return "N/A"
        return f"{p.get('start')} - {p.get('end')}"

    print("Inauspicious Times")
    print(format_field("Rahu Kaal", fmt_period(rahu)))
    print(format_field("Yamaganda", fmt_period(yama)))
    print(format_field("Gulika", fmt_period(gulika)))
    print()

    # Auspicious times
    aus = data.get("auspicious_times", {})
    abhijit = aus.get("abhijit_muhurat", {})
    brahma = aus.get("brahma_muhurat", {})
    amrita = aus.get("amrita_kalam", {})

    print("Auspicious Times")
    print(format_field("Abhijit", fmt_period(abhijit)))
    print(format_field("Brahma Muhurta", fmt_period(brahma)))
    print(format_field("Amrita Kalam", fmt_period(amrita)))
    print()

    # Festivals / notes (English only for quick comparison)
    specials = data.get("south_india_special", []) or []
    if specials:
        print("Festivals / Notes (South India)")
        for item in specials:
            etype = item.get("type", "note")
            text = item.get("english") or item.get("text")
            print(f"- [{etype}] {text}")
        print()

    print("=== End of Panchang Output ===")


def main() -> None:
    parser = argparse.ArgumentParser(description="Internal Panchang calibration runner")
    parser.add_argument(
        "--date",
        required=True,
        help="Date in YYYY-MM-DD (e.g. 2025-12-01)",
    )
    parser.add_argument(
        "--lat",
        type=float,
        default=12.9716,
        help="Latitude (default: 12.9716 for Bengaluru)",
    )
    parser.add_argument(
        "--lon",
        type=float,
        default=77.5946,
        help="Longitude (default: 77.5946 for Bengaluru)",
    )
    parser.add_argument(
        "--city",
        default="Bengaluru",
        help="City name label (default: Bengaluru)",
    )

    args = parser.parse_args()
    run(args.date, args.lat, args.lon, args.city)


if __name__ == "__main__":
    main()













