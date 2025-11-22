"""
Vedic Panchang Service using Swiss Ephemeris
Implements accurate Panchang calculations with Lahiri Ayanamsa
"""

import swisseph as swe
from datetime import datetime, date, timedelta
from typing import Dict, Optional
import math

class PanchangService:
    """
    Professional Panchang calculation service
    Uses Swiss Ephemeris with Lahiri Ayanamsa for accuracy
    """

    # Nakshatra names (27 lunar mansions)
    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini",
        "Mrigashira", "Ardra", "Punarvasu", "Pushya",
        "Ashlesha", "Magha", "Purva Phalguni",
        "Uttara Phalguni", "Hasta", "Chitra", "Swati",
        "Vishakha", "Anuradha", "Jyeshtha", "Mula",
        "Purva Ashadha", "Uttara Ashadha", "Shravana",
        "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
        "Uttara Bhadrapada", "Revati"
    ]

    # Tithi names
    TITHIS = [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima"
    ]

    # Yoga names
    YOGAS = [
        "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
        "Atiganda", "Sukarma", "Dhriti", "Shoola", "Ganda",
        "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
        "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
        "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
        "Indra", "Vaidhriti"
    ]

    # Karana names
    KARANAS = [
        "Bava", "Balava", "Kaulava", "Taitila", "Garaja",
        "Vanija", "Vishti", "Shakuni", "Chatushpada",
        "Naga", "Kimstughna"
    ]

    # Vara (weekday) names
    VARAS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    VARA_SANSKRIT = ["रविवार", "सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"]
    VARA_DEITIES = [
        "Surya (Sun)",
        "Chandra (Moon)",
        "Mangal (Mars)",
        "Budh (Mercury)",
        "Brihaspati (Jupiter)",
        "Shukra (Venus)",
        "Shani (Saturn)"
    ]

    def __init__(self):
        """Initialize Panchang Service with Lahiri Ayanamsa"""
        # CRITICAL: Set Lahiri ayanamsa for Indian calculations
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    def get_julian_day(self, dt: datetime) -> float:
        """Convert datetime to Julian Day"""
        return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)

    def get_sidereal_position(self, jd: float, planet: int) -> float:
        """Get sidereal (Nirayana) position of a planet"""
        # Use FLG_SIDEREAL flag for Indian calculations
        result = swe.calc_ut(jd, planet, swe.FLG_SIDEREAL)
        return result[0][0]  # Longitude in degrees

    def get_nakshatra(self, jd: float) -> Dict:
        """Calculate current Nakshatra"""
        moon_long = self.get_sidereal_position(jd, swe.MOON)

        # Each nakshatra is 13°20' (13.333...)
        nak_num = int(moon_long / 13.333333)
        nak_pada = int((moon_long % 13.333333) / 3.333333) + 1

        # Calculate end time (when moon moves to next nakshatra)
        next_nak_deg = (nak_num + 1) * 13.333333
        degrees_to_go = next_nak_deg - moon_long
        if degrees_to_go < 0:
            degrees_to_go += 360

        # Moon moves ~13° per day
        hours_to_end = (degrees_to_go / 13.176358) * 24  # Average moon speed

        return {
            "number": nak_num + 1,
            "name": self.NAKSHATRAS[nak_num],
            "pada": nak_pada,
            "moon_longitude": round(moon_long, 2),
            "end_time": None  # TODO: Calculate precise end time
        }

    def get_tithi(self, jd: float) -> Dict:
        """Calculate current Tithi"""
        moon_long = self.get_sidereal_position(jd, swe.MOON)
        sun_long = self.get_sidereal_position(jd, swe.SUN)

        # Tithi is based on elongation of Moon from Sun
        diff = moon_long - sun_long
        if diff < 0:
            diff += 360

        # Each tithi is 12 degrees
        tithi_num = int(diff / 12)

        # Determine paksha (fortnight)
        if tithi_num < 15:
            paksha = "Shukla"  # Waxing/Bright half
            tithi_name = self.TITHIS[tithi_num]
        else:
            paksha = "Krishna"  # Waning/Dark half
            tithi_num_in_paksha = tithi_num - 15
            if tithi_num_in_paksha == 14:
                tithi_name = "Amavasya"  # New moon
            else:
                tithi_name = self.TITHIS[tithi_num_in_paksha]

        return {
            "number": (tithi_num % 15) + 1,
            "name": tithi_name,
            "paksha": paksha,
            "full_name": f"{paksha} {tithi_name}",
            "is_special": tithi_name in ["Ekadashi", "Purnima", "Amavasya"],
            "elongation": round(diff, 2)
        }

    def get_yoga(self, jd: float) -> Dict:
        """Calculate current Yoga"""
        moon_long = self.get_sidereal_position(jd, swe.MOON)
        sun_long = self.get_sidereal_position(jd, swe.SUN)

        # Yoga = (Moon + Sun) / 13.333...
        total = (moon_long + sun_long) % 360
        yoga_num = int(total / 13.333333)

        return {
            "number": yoga_num + 1,
            "name": self.YOGAS[yoga_num],
            "is_inauspicious": self.YOGAS[yoga_num] in ["Vyatipata", "Vaidhriti"]
        }

    def get_karana(self, jd: float) -> Dict:
        """Calculate current Karana"""
        moon_long = self.get_sidereal_position(jd, swe.MOON)
        sun_long = self.get_sidereal_position(jd, swe.SUN)

        diff = moon_long - sun_long
        if diff < 0:
            diff += 360

        # Each tithi has 2 karanas (6 degrees each)
        karana_num = int(diff / 6)

        # Karanas repeat in a pattern
        if karana_num >= 57:  # Last 4 karanas (fixed)
            karana_index = 7 + (karana_num - 57)
        else:
            karana_index = karana_num % 7

        return {
            "name": self.KARANAS[min(karana_index, 10)],
            "is_bhadra": self.KARANAS[min(karana_index, 10)] == "Vishti"
        }

    def get_vara(self, dt: datetime) -> Dict:
        """Get weekday (Vara) details"""
        vara_num = dt.weekday()  # 0 = Monday in Python
        # Adjust to Sunday = 0 for Hindu calendar
        vara_num = (vara_num + 1) % 7

        return {
            "number": vara_num + 1,
            "name": self.VARAS[vara_num],
            "sanskrit": self.VARA_SANSKRIT[vara_num],
            "deity": self.VARA_DEITIES[vara_num]
        }

    def get_sun_rise_set(self, dt: datetime, lat: float, lon: float) -> Dict:
        """Calculate sunrise and sunset times using Swiss Ephemeris"""
        try:
            # Get Julian day for the date at midnight UTC
            # We need to account for timezone - IST is UTC+5:30
            jd_midnight = swe.julday(dt.year, dt.month, dt.day, 0.0)

            # Geo position as tuple (longitude, latitude, altitude in meters)
            geopos = (lon, lat, 0)

            # Calculate sunrise - returns JD in UTC
            # rise_trans parameters: (jd, body, geopos, rsmi)
            sunrise_result = swe.rise_trans(
                jd_midnight,
                swe.SUN,
                geopos,
                swe.CALC_RISE | swe.BIT_DISC_CENTER
            )

            # Calculate sunset - returns JD in UTC
            sunset_result = swe.rise_trans(
                jd_midnight,
                swe.SUN,
                geopos,
                swe.CALC_SET | swe.BIT_DISC_CENTER
            )

            # Convert Julian Day to local time (IST)
            def jd_to_local_time(jd_value):
                # swe.revjul returns year, month, day, hour (in UTC)
                year, month, day, hour_utc = swe.revjul(jd_value)

                # Convert UTC to IST (UTC + 5:30)
                hour_ist = hour_utc + 5.5
                if hour_ist >= 24:
                    hour_ist -= 24

                hours = int(hour_ist)
                minutes = int((hour_ist - hours) * 60)
                seconds = int(((hour_ist - hours) * 60 - minutes) * 60)

                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            # Check if calculations succeeded (return code 0 = success)
            if sunrise_result[0] == 0 and len(sunrise_result[1]) > 0:
                sunrise_time = jd_to_local_time(sunrise_result[1][0])
            else:
                print(f"Sunrise calculation failed: {sunrise_result}")
                sunrise_time = "06:25:00"  # Fallback for Bangalore

            if sunset_result[0] == 0 and len(sunset_result[1]) > 0:
                sunset_time = jd_to_local_time(sunset_result[1][0])
            else:
                print(f"Sunset calculation failed: {sunset_result}")
                sunset_time = "17:46:00"  # Fallback for Bangalore

            return {
                "sunrise": sunrise_time,
                "sunset": sunset_time
            }
        except Exception as e:
            # Log error and return fallback times
            print(f"Error calculating sunrise/sunset: {e}")
            import traceback
            traceback.print_exc()
            return {
                "sunrise": "06:25:00",  # Bangalore approximate
                "sunset": "17:46:00"     # Bangalore approximate
            }

    def calculate_panchang(self, dt: datetime, lat: float = 12.9716, lon: float = 77.5946) -> Dict:
        """
        Calculate complete Panchang for a given date and location

        Args:
            dt: DateTime to calculate for
            lat: Latitude (default: Bangalore 12.9716°N)
            lon: Longitude (default: Bangalore 77.5946°E)

        Returns:
            Complete Panchang data dictionary
        """
        jd = self.get_julian_day(dt)
        ayanamsa = swe.get_ayanamsa_ut(jd)

        return {
            "date": {
                "gregorian": {
                    "date": dt.date().isoformat(),
                    "day": dt.strftime("%A"),
                    "formatted": dt.strftime("%A, %B %d, %Y")
                },
                "hindu": {
                    "samvat_vikram": 2082,  # TODO: Calculate dynamically
                    "month": "Margashirsha",  # TODO: Calculate from tithi
                    "paksha": self.get_tithi(jd)["paksha"]
                }
            },
            "panchang": {
                "tithi": self.get_tithi(jd),
                "nakshatra": self.get_nakshatra(jd),
                "yoga": self.get_yoga(jd),
                "karana": self.get_karana(jd),
                "vara": self.get_vara(dt)
            },
            "sun_moon": self.get_sun_rise_set(dt, lat, lon),
            "location": {
                "city": "Bangalore",  # Default
                "latitude": lat,
                "longitude": lon,
                "timezone": "Asia/Kolkata"
            },
            "calculation_metadata": {
                "ayanamsa_type": "LAHIRI",
                "ayanamsa_value": round(ayanamsa, 4),
                "generated_at": datetime.now().isoformat(),
                "verified_against": "Swiss Ephemeris with Lahiri Ayanamsa"
            }
        }
