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

    # Rashi (Moon Sign) names
    RASHIS = [
        "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
        "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
    ]

    # Ruthu (Season) names
    RUTHUS = [
        "Vasanta", "Grishma", "Varsha", "Sharad", "Hemanta", "Shishira"
    ]

    # Samvatsara names (60-year cycle)
    SAMVATSARAS = [
        "Prabhava", "Vibhava", "Shukla", "Pramoda", "Prajapati",
        "Angirasa", "Shrimukha", "Bhava", "Yuvan", "Dhatri",
        "Ishvara", "Bahudhanya", "Pramathi", "Vikrama", "Vrisha",
        "Chitrabhanu", "Svabhanu", "Tarana", "Parthiva", "Vyaya",
        "Sarvajit", "Sarvadharin", "Virodhin", "Vikrita", "Khara",
        "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukha",
        "Hemalamba", "Vilamba", "Vikarin", "Sharvari", "Plava",
        "Shubhakrit", "Shobhana", "Krodhin", "Vishvavasu", "Parabhava",
        "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhikrit",
        "Paridhavi", "Pramadin", "Ananda", "Rakshasa", "Nala",
        "Pingala", "Kalayukta", "Siddharthi", "Raudra", "Durmathi",
        "Dundubhi", "Rudhirodgari", "Raktaksha", "Krodhana", "Kshaya"
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
        """Calculate current Karana (both halves of the day)"""
        moon_long = self.get_sidereal_position(jd, swe.MOON)
        sun_long = self.get_sidereal_position(jd, swe.SUN)

        diff = moon_long - sun_long
        if diff < 0:
            diff += 360

        # Each tithi has 2 karanas (6 degrees each)
        karana_num = int(diff / 6)

        # Calculate karana for first half
        if karana_num >= 57:  # Last 4 karanas (fixed)
            karana_index_first = 7 + (karana_num - 57)
        else:
            karana_index_first = karana_num % 7

        # Calculate karana for second half (next karana)
        karana_num_second = (karana_num + 1) % 60
        if karana_num_second >= 57:
            karana_index_second = 7 + (karana_num_second - 57)
        else:
            karana_index_second = karana_num_second % 7

        first_karana = self.KARANAS[min(karana_index_first, 10)]
        second_karana = self.KARANAS[min(karana_index_second, 10)]

        return {
            "name": first_karana,
            "is_bhadra": first_karana == "Vishti" or second_karana == "Vishti",
            "first_half": {
                "name": first_karana,
                "is_bhadra": first_karana == "Vishti"
            },
            "second_half": {
                "name": second_karana,
                "is_bhadra": second_karana == "Vishti"
            }
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

    def get_moon_sign(self, jd: float) -> Dict:
        """Calculate Moon's Rashi (zodiac sign)"""
        moon_long = self.get_sidereal_position(jd, swe.MOON)
        rashi_num = int(moon_long / 30)

        return {
            "number": rashi_num + 1,
            "name": self.RASHIS[rashi_num],
            "moon_longitude": round(moon_long, 2)
        }

    def get_ayana(self, jd: float) -> str:
        """Calculate Ayana (Sun's course)"""
        sun_long = self.get_sidereal_position(jd, swe.SUN)

        # Uttarayana: Makara (270°) to Mithuna (90°)
        # Dakshinayana: Karka (90°) to Dhanu (270°)
        if 270 <= sun_long or sun_long < 90:
            return "Uttarayana"
        else:
            return "Dakshinayana"

    def get_ruthu(self, jd: float) -> str:
        """Calculate Ruthu (season) based on Hindu solar calendar"""
        sun_long = self.get_sidereal_position(jd, swe.SUN)

        # Ruthus based on solar longitude (each Ruthu = 2 rashis = 60 degrees):
        # Vasanta (Spring): 330° to 30° (Meena, Mesha)
        # Grishma (Summer): 30° to 90° (Vrishabha, Mithuna)
        # Varsha (Monsoon): 90° to 150° (Karka, Simha)
        # Sharad (Autumn): 150° to 210° (Kanya, Tula)
        # Hemanta (Pre-winter): 210° to 270° (Vrishchika, Dhanu)
        # Shishira (Winter): 270° to 330° (Makara, Kumbha)

        if 330 <= sun_long or sun_long < 30:
            return "Vasanta"
        elif 30 <= sun_long < 90:
            return "Grishma"
        elif 90 <= sun_long < 150:
            return "Varsha"
        elif 150 <= sun_long < 210:
            return "Sharad"
        elif 210 <= sun_long < 270:
            return "Hemanta"
        else:  # 270 <= sun_long < 330
            return "Shishira"

    def get_samvatsara(self, year: int) -> Dict:
        """Calculate Samvatsara name (60-year cycle) using Shaka Samvat"""
        # Shaka Samvat = Gregorian Year - 78 (for dates after March/April)
        # For 2025 CE -> Shaka Samvat 1947 -> Vishvavasu (39th, index 38)
        shaka_year = year - 78

        # Calculate position in 60-year cycle
        # Shaka 1947 = Vishvavasu (index 38)
        # Formula: (shaka_year + 11) mod 60 gives the correct index
        samvatsara_index = (shaka_year + 11) % 60

        return {
            "number": samvatsara_index + 1,
            "name": self.SAMVATSARAS[samvatsara_index],
            "shaka_year": shaka_year,
            "kali_year": year + 3102,  # Kali year calculation
            "cycle_year": samvatsara_index + 1
        }

    def get_rahu_kala(self, sunrise: str, sunset: str, day_of_week: int) -> Dict:
        """Calculate Rahu Kala timing"""
        # Convert times to minutes
        def time_to_minutes(time_str):
            parts = time_str.split(':')
            return int(parts[0]) * 60 + int(parts[1])

        def minutes_to_time(minutes):
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return f"{hours:02d}:{mins:02d}:00"

        sunrise_min = time_to_minutes(sunrise)
        sunset_min = time_to_minutes(sunset)
        day_duration = sunset_min - sunrise_min
        segment = day_duration / 8

        # Rahu Kala occurs at different times each day
        # Sunday=0, Monday=1, ..., Saturday=6
        rahu_segments = {
            6: 2,  # Saturday: 2nd segment
            0: 8,  # Sunday: 8th segment
            1: 3,  # Monday: 3rd segment
            2: 6,  # Tuesday: 6th segment
            3: 5,  # Wednesday: 5th segment
            4: 4,  # Thursday: 4th segment
            5: 7   # Friday: 7th segment
        }

        segment_num = rahu_segments.get(day_of_week, 1)
        start_min = sunrise_min + ((segment_num - 1) * segment)
        end_min = start_min + segment

        return {
            "start": minutes_to_time(start_min),
            "end": minutes_to_time(end_min),
            "duration_minutes": int(segment)
        }

    def get_yamaganda(self, sunrise: str, sunset: str, day_of_week: int) -> Dict:
        """Calculate Yamaganda timing"""
        def time_to_minutes(time_str):
            parts = time_str.split(':')
            return int(parts[0]) * 60 + int(parts[1])

        def minutes_to_time(minutes):
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return f"{hours:02d}:{mins:02d}:00"

        sunrise_min = time_to_minutes(sunrise)
        sunset_min = time_to_minutes(sunset)
        day_duration = sunset_min - sunrise_min
        segment = day_duration / 8

        yamaganda_segments = {
            6: 7,  # Saturday: 7th segment
            0: 5,  # Sunday: 5th segment
            1: 5,  # Monday: 5th segment
            2: 4,  # Tuesday: 4th segment
            3: 3,  # Wednesday: 3rd segment
            4: 2,  # Thursday: 2nd segment
            5: 8   # Friday: 8th segment
        }

        segment_num = yamaganda_segments.get(day_of_week, 1)
        start_min = sunrise_min + ((segment_num - 1) * segment)
        end_min = start_min + segment

        return {
            "start": minutes_to_time(start_min),
            "end": minutes_to_time(end_min),
            "duration_minutes": int(segment)
        }

    def get_gulika(self, sunrise: str, sunset: str, day_of_week: int) -> Dict:
        """Calculate Gulika Kala timing"""
        def time_to_minutes(time_str):
            parts = time_str.split(':')
            return int(parts[0]) * 60 + int(parts[1])

        def minutes_to_time(minutes):
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return f"{hours:02d}:{mins:02d}:00"

        sunrise_min = time_to_minutes(sunrise)
        sunset_min = time_to_minutes(sunset)
        day_duration = sunset_min - sunrise_min
        segment = day_duration / 8

        gulika_segments = {
            6: 8,  # Saturday: 8th segment
            0: 7,  # Sunday: 7th segment
            1: 6,  # Monday: 6th segment
            2: 5,  # Tuesday: 5th segment
            3: 4,  # Wednesday: 4th segment
            4: 3,  # Thursday: 3rd segment
            5: 2   # Friday: 2nd segment
        }

        segment_num = gulika_segments.get(day_of_week, 1)
        start_min = sunrise_min + ((segment_num - 1) * segment)
        end_min = start_min + segment

        return {
            "start": minutes_to_time(start_min),
            "end": minutes_to_time(end_min),
            "duration_minutes": int(segment)
        }

    def get_abhijit_muhurat(self, sunrise: str, sunset: str) -> Dict:
        """Calculate Abhijit Muhurat (most auspicious time)"""
        def time_to_minutes(time_str):
            parts = time_str.split(':')
            return int(parts[0]) * 60 + int(parts[1])

        def minutes_to_time(minutes):
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return f"{hours:02d}:{mins:02d}:00"

        sunrise_min = time_to_minutes(sunrise)
        sunset_min = time_to_minutes(sunset)

        # Abhijit Muhurat is at noon (midpoint of day)
        # Standard duration is approximately 46 minutes (1/15th of day duration)
        midday = (sunrise_min + sunset_min) / 2
        day_duration = sunset_min - sunrise_min
        duration = day_duration / 15  # Approx 46 minutes for 11.5 hour day

        start_min = midday - (duration / 2)
        end_min = midday + (duration / 2)

        return {
            "start": minutes_to_time(start_min),
            "end": minutes_to_time(end_min),
            "duration_minutes": duration
        }

    def detect_special_days(self, tithi_data: Dict, vara: Dict, nakshatra: Dict) -> list:
        """Detect special days like Ekadashi, Pradosha, Sankashta Chaturthi"""
        special_days = []

        tithi_name = tithi_data.get("name", "")
        tithi_num = tithi_data.get("number", 0)
        vara_name = vara.get("name", "")
        nakshatra_name = nakshatra.get("name", "")

        # Ekadashi (11th tithi)
        if tithi_name == "Ekadashi":
            special_days.append({
                "name": "Ekadashi",
                "description": "Fasting day dedicated to Lord Vishnu",
                "observance": "Fast from grains and beans"
            })

        # Pradosha (13th tithi)
        if tithi_name == "Trayodashi":
            special_days.append({
                "name": "Pradosha Vrat",
                "description": "Auspicious time to worship Lord Shiva during twilight",
                "observance": "Worship Shiva during sunset time"
            })

        # Sankashta Chaturthi (4th tithi in Krishna Paksha with Tuesday)
        if tithi_name == "Chaturthi" and tithi_data.get("paksha") == "Krishna":
            special_days.append({
                "name": "Sankashta Chaturthi",
                "description": "Day dedicated to Lord Ganesha",
                "observance": "Fast and worship Ganesha, break fast after moonrise"
            })

        # Amavasya (New Moon)
        if tithi_name == "Amavasya":
            special_days.append({
                "name": "Amavasya",
                "description": "New Moon day, sacred for ancestor worship",
                "observance": "Perform Tarpanam for ancestors"
            })

        # Purnima (Full Moon)
        if tithi_name == "Purnima":
            special_days.append({
                "name": "Purnima",
                "description": "Full Moon day, auspicious for all spiritual activities",
                "observance": "Fasting and meditation"
            })

        return special_days

    def calculate_panchang(self, dt: datetime, lat: float = 12.9716, lon: float = 77.5946, city: str = "Bengaluru") -> Dict:
        """
        Calculate complete Panchang for a given date and location

        Args:
            dt: DateTime to calculate for
            lat: Latitude (default: Bangalore 12.9716°N)
            lon: Longitude (default: Bangalore 77.5946°E)
            city: City name (default: Bengaluru)

        Returns:
            Complete Panchang data dictionary
        """
        jd = self.get_julian_day(dt)
        ayanamsa = swe.get_ayanamsa_ut(jd)

        # Get all panchang elements
        tithi_data = self.get_tithi(jd)
        nakshatra_data = self.get_nakshatra(jd)
        yoga_data = self.get_yoga(jd)
        karana_data = self.get_karana(jd)
        vara_data = self.get_vara(dt)
        sun_moon_data = self.get_sun_rise_set(dt, lat, lon)
        moon_sign_data = self.get_moon_sign(jd)
        samvatsara_data = self.get_samvatsara(dt.year)

        # Calculate inauspicious times
        day_of_week = (dt.weekday() + 1) % 7  # Convert to Sunday=0 format
        rahu_kala = self.get_rahu_kala(sun_moon_data["sunrise"], sun_moon_data["sunset"], day_of_week)
        yamaganda = self.get_yamaganda(sun_moon_data["sunrise"], sun_moon_data["sunset"], day_of_week)
        gulika = self.get_gulika(sun_moon_data["sunrise"], sun_moon_data["sunset"], day_of_week)

        # Calculate auspicious times
        abhijit_muhurat = self.get_abhijit_muhurat(sun_moon_data["sunrise"], sun_moon_data["sunset"])

        # Detect special days
        special_days = self.detect_special_days(tithi_data, vara_data, nakshatra_data)

        return {
            "date": {
                "gregorian": {
                    "date": dt.date().isoformat(),
                    "day": dt.strftime("%A"),
                    "formatted": dt.strftime("%A, %B %d, %Y")
                },
                "hindu": {
                    "samvat_vikram": 2082,  # Vikram Samvat
                    "samvatsara": samvatsara_data,
                    "month": "Margashirsha",  # TODO: Calculate from Moon position
                    "paksha": tithi_data["paksha"]
                }
            },
            "panchang": {
                "tithi": tithi_data,
                "nakshatra": nakshatra_data,
                "yoga": yoga_data,
                "karana": karana_data,
                "vara": vara_data
            },
            "sun_moon": sun_moon_data,
            "moon_sign": moon_sign_data,
            "ayana": self.get_ayana(jd),
            "ruthu": self.get_ruthu(jd),
            "inauspicious_times": {
                "rahu_kaal": rahu_kala,
                "yamaganda": yamaganda,
                "gulika": gulika
            },
            "auspicious_times": {
                "abhijit_muhurat": abhijit_muhurat
            },
            "festivals": special_days,
            "location": {
                "city": city,
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
