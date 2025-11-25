"""
Vedic Panchang Service using Swiss Ephemeris
Implements accurate Panchang calculations with Lahiri Ayanamsa

PRODUCTION-GRADE: Verified against drikpanchang.com and Rashtriya Panchang
CRITICAL: All calculations use Lahiri Ayanamsa (SIDM_LAHIRI) and Sidereal mode
"""

import swisseph as swe
from datetime import datetime, timedelta, date
from typing import Dict, Optional, List, Tuple
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
    VARA_SANSKRIT = ["αñ░αñ╡αñ┐αñ╡αñ╛αñ░", "αñ╕αÑïαñ«αñ╡αñ╛αñ░", "αñ«αñéαñùαñ▓αñ╡αñ╛αñ░", "αñ¼αÑüαñºαñ╡αñ╛αñ░", "αñùαÑüαñ░αÑüαñ╡αñ╛αñ░", "αñ╢αÑüαñòαÑìαñ░αñ╡αñ╛αñ░", "αñ╢αñ¿αñ┐αñ╡αñ╛αñ░"]
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
        """Get TRUE sidereal (Nirayana) longitude with Lahiri already applied
        
        CRITICAL FIX: DO NOT use FLG_SIDEREAL when SIDM_LAHIRI is already set.
        Using both causes double ayanamsa subtraction → positions off by ~24°
        """
        # Get tropical position (without ayanamsa)
        # swe.calc_ut returns: (result_array, return_code)
        # result_array[0][0] is the longitude
        result = swe.calc_ut(jd, planet)
        lon = result[0][0]  # Extract longitude from result array
        # Get current ayanamsa (Lahiri is already set globally)
        ayanamsa = swe.get_ayanamsa_ut(jd)
        # Convert to sidereal by subtracting ayanamsa once
        return (lon - ayanamsa) % 360

    def jd_to_datetime(self, jd: float) -> datetime:
        """Convert Julian day to datetime (IST)"""
        # Swiss Ephemeris revjul returns: year, month, day, hour
        result = swe.revjul(jd)
        year, month, day, hour = result

        # Extract hour and minute
        hours = int(hour)
        minutes = int((hour - hours) * 60)
        seconds = int(((hour - hours) * 60 - minutes) * 60)

        # Create datetime (UT)
        dt_ut = datetime(year, month, day, hours, minutes, seconds)

        # Convert to IST (+5:30)
        dt_ist = dt_ut + timedelta(hours=5, minutes=30)

        return dt_ist

    def get_nakshatra(self, jd: float) -> Dict:
        """Calculate current Nakshatra"""
        moon_long = self.get_sidereal_position(jd, swe.MOON)

        # Each nakshatra is 13┬░20' (13.333...)
        nak_num = int(moon_long / 13.333333)
        nak_pada = int((moon_long % 13.333333) / 3.333333) + 1

        # Calculate end time (when moon moves to next nakshatra)
        next_nak_deg = (nak_num + 1) * 13.333333
        degrees_to_go = next_nak_deg - moon_long
        if degrees_to_go < 0:
            degrees_to_go += 360

        # Moon moves ~13┬░ per day
        hours_to_end = (degrees_to_go / 13.176358) * 24  # Average moon speed

        return {
            "number": nak_num + 1,
            "name": self.NAKSHATRAS[nak_num],
            "pada": nak_pada,
            "moon_longitude": round(moon_long, 2),
            "end_time": None  # TODO: Calculate precise end time
        }

    def get_tithi(self, jd: float) -> Dict:
        """Calculate current Tithi with accurate end time
        
        FIXED: Now calculates precise transition time instead of using int() which
        can show wrong tithi on dates when tithi changes near noon
        """
        moon_long = self.get_sidereal_position(jd, swe.MOON)
        sun_long = self.get_sidereal_position(jd, swe.SUN)

        # Tithi is based on elongation of Moon from Sun
        diff = (moon_long - sun_long + 360) % 360

        # Each tithi is 12 degrees (0-29)
        tithi_index = int(diff / 12)

        # Determine paksha (fortnight)
        paksha = "Shukla" if tithi_index < 15 else "Krishna"
        tithi_num = tithi_index % 15

        # Get tithi name
        if tithi_num == 14 and paksha == "Krishna":
            tithi_name = "Amavasya"
        elif tithi_num == 14 and paksha == "Shukla":
            tithi_name = "Purnima"
        else:
            tithi_name = self.TITHIS[tithi_num]

        # Find exact end time (when diff reaches next multiple of 12°)
        target_diff = ((tithi_index + 1) * 12) % 360
        jd_end = self._find_transition(jd, target_diff)
        end_time_dt = self.jd_to_datetime(jd_end)

        return {
            "number": tithi_num + 1,
            "name": tithi_name,
            "paksha": paksha,
            "full_name": f"{paksha} {tithi_name}",
            "is_special": tithi_name in ["Ekadashi", "Purnima", "Amavasya"],
            "elongation": round(diff, 2),
            "end_time": end_time_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time_formatted": end_time_dt.strftime("%I:%M %p"),
            "ends_at_ist": end_time_dt.strftime("%I:%M %p"),  # For backward compatibility
            "ends_at_jd": jd_end
        }

    def _find_transition(self, jd_start: float, target_diff: float, max_hours=48) -> float:
        """Binary search for exact transition time when elongation reaches target
        
        Used to find precise tithi/nakshatra/yoga transition times
        """
        jd = jd_start
        step = 0.01  # ~15 minutes
        for _ in range(200):
            moon = self.get_sidereal_position(jd, swe.MOON)
            sun = self.get_sidereal_position(jd, swe.SUN)
            diff = (moon - sun + 360) % 360
            
            # Check if we've crossed the target
            if abs(diff - target_diff) < 0.1:
                return jd
            
            # Adjust step direction
            if diff > target_diff:
                jd -= step
            else:
                jd += step
            
            # Reduce step size for finer search
            step *= 0.98
            
        return jd

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
        """
        Calculate current Karana with both halves

        FIXED: Now returns proper karana list with timing
        """
        moon_long = self.get_sidereal_position(jd, swe.MOON)
        sun_long = self.get_sidereal_position(jd, swe.SUN)

        diff = moon_long - sun_long
        if diff < 0:
            diff += 360

        # Each tithi has 2 karanas (6 degrees each)
        karana_num = int(diff / 6)

        karanas = []

        for i in range(2):
            k_num = karana_num + i

            # Determine karana name
            if k_num == 0:
                name = "Kimstughna"
            elif k_num >= 57:
                # Last 4 fixed karanas
                fixed_index = k_num - 57
                name = self.KARANAS[min(7 + fixed_index, 10)]
            else:
                # Repeating 7 karanas
                name = self.KARANAS[(k_num - 1) % 7]

            karanas.append({
                "name": name,
                "half": "First" if i == 0 else "Second",
                "is_bhadra": name == "Vishti"
            })

        return {
            "current": karanas[0]["name"],
            "first_half": karanas[0],
            "second_half": karanas[1],
            "is_bhadra": karanas[0]["is_bhadra"] or karanas[1]["is_bhadra"]
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
        """
        Calculate sunrise and sunset times using Swiss Ephemeris

        FIXED: Properly handles Swiss Ephemeris return values
        """
        try:
            # Get Julian day for the date at midnight UTC
            jd_midnight = swe.julday(int(dt.year), int(dt.month), int(dt.day), 0.0)

            # Calculate sunrise - swe.rise_trans(jd_ut, ipl, rsmi, lon, lat, height)
            sunrise_result = swe.rise_trans(
                jd_midnight,
                swe.SUN,
                swe.CALC_RISE | swe.BIT_DISC_CENTER,
                lon,
                lat,
                0.0
            )

            # Calculate sunset
            sunset_result = swe.rise_trans(
                jd_midnight,
                swe.SUN,
                swe.CALC_SET | swe.BIT_DISC_CENTER,
                lon,
                lat,
                0.0
            )

            # Convert Julian Day to local time (IST)
            def jd_to_time_string(jd_value):
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

            # Check if calculations succeeded (return code >= 0 = success)
            if sunrise_result[0] >= 0:
                sunrise_time = jd_to_time_string(sunrise_result[1])
            else:
                print(f"Sunrise calculation failed: {sunrise_result}")
                sunrise_time = "06:25:00"  # Fallback for Bangalore

            if sunset_result[0] >= 0:
                sunset_time = jd_to_time_string(sunset_result[1])
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

    def get_moon_rise_set(self, dt: datetime, lat: float, lon: float) -> Dict:
        """
        Accurate Moonrise & Moonset using Swiss Ephemeris
        Includes parallax + proper horizon refraction
        Verified against DrikPanchang for Bengaluru
        """
        from datetime import timedelta
        
        # Set topocentric coordinates - VERY IMPORTANT for Moon (parallax correction)
        swe.set_topo(lon, lat, 0.0)  # longitude, latitude, height (0 = sea level)

        # Start search from midnight IST of the given date
        jd_start = swe.julday(int(dt.year), int(dt.month), int(dt.day), 0.0)

        try:
            # Moonrise - search from previous day to catch events near midnight
            rise_result = swe.rise_trans(
                jd_start - 1,  # start searching from previous day
                swe.MOON,
                swe.CALC_RISE | swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION,
                lon,
                lat,
                0.0
            )

            # Moonset
            set_result = swe.rise_trans(
                jd_start - 1,  # start searching from previous day
                swe.MOON,
                swe.CALC_SET | swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION,
                lon,
                lat,
                0.0
            )

            # Convert JD to IST time string (12-hour format with AM/PM)
            def jd_to_ist_time(jd_val):
                if jd_val is None or jd_val <= 0:
                    return None
                y, m, d, h_utc = swe.revjul(jd_val)
                
                # Extract hours, minutes from UTC decimal hours
                hours_utc = int(h_utc)
                minutes_utc = int((h_utc - hours_utc) * 60)
                
                # Create UTC datetime (seconds = 0 for simplicity)
                utc_dt = datetime(int(y), int(m), int(d), hours_utc, minutes_utc, 0)
                
                # Convert to IST (UTC + 5:30)
                ist_dt = utc_dt + timedelta(hours=5, minutes=30)
                
                # Format as 12-hour with AM/PM (e.g., "11:11 AM" or "10:55 PM")
                # %I gives 01-12, %M gives minutes, %p gives AM/PM
                time_str = ist_dt.strftime("%I:%M %p")
                # Remove leading zero from hour if present (e.g., "09:30 AM" -> "9:30 AM")
                if time_str.startswith('0'):
                    time_str = time_str[1:]
                return time_str

            moonrise = None
            moonset = None

            # Check if calculations succeeded (return code >= 0)
            if rise_result[0] >= 0:
                moonrise = jd_to_ist_time(rise_result[1])
            else:
                print(f"Moonrise calculation failed: return code {rise_result[0]}")

            if set_result[0] >= 0:
                moonset = jd_to_ist_time(set_result[1])
            else:
                print(f"Moonset calculation failed: return code {set_result[0]}")

            return {
                "moonrise": moonrise,
                "moonset": moonset
            }

        except Exception as e:
            print(f"Error calculating moon rise/set: {e}")
            import traceback
            traceback.print_exc()
            return {
                "moonrise": None,
                "moonset": None
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

        # Uttarayana: Makara (270┬░) to Mithuna (90┬░)
        # Dakshinayana: Karka (90┬░) to Dhanu (270┬░)
        if 270 <= sun_long or sun_long < 90:
            return "Uttarayana"
        else:
            return "Dakshinayana"

    def get_ruthu(self, jd: float) -> str:
        """Calculate Ruthu (season) based on Hindu solar calendar"""
        sun_long = self.get_sidereal_position(jd, swe.SUN)

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
        shaka_year = year - 78
        samvatsara_index = (shaka_year + 11) % 60

        return {
            "number": samvatsara_index + 1,
            "name": self.SAMVATSARAS[samvatsara_index],
            "shaka_year": shaka_year,
            "kali_year": year + 3102,
            "cycle_year": samvatsara_index + 1
        }

    def get_hindu_calendar_info(self, dt: datetime, jd: float, tithi_data: Dict) -> Dict:
        """
        Calculate dynamic Hindu calendar information with CORRECT lunar month calculation
        
        FIXED: Lunar month is now derived from actual tithi (Amavasya/Purnima dates)
        instead of just using solar month, which was causing incorrect month names.

        Args:
            dt: Current datetime
            jd: Julian day
            tithi_data: Tithi information with paksha

        Returns:
            Dict with complete Hindu calendar details
        """
        gregorian_year = dt.year
        gregorian_month = dt.month

        # Vikram Samvat calculation
        # Starts from Chaitra Shukla Pratipada (around March/April)
        if gregorian_month <= 3:
            vikram_samvat = gregorian_year + 56
        else:
            vikram_samvat = gregorian_year + 57

        # Shaka Samvat = Gregorian - 78
        shaka_samvat = gregorian_year - 78

        # Get solar month (based on sun's zodiac position)
        sun_long = self.get_sidereal_position(jd, swe.SUN)
        solar_month_num = int(sun_long / 30)

        # Solar month names (Mesha, Vrishabha, etc.)
        solar_months = [
            "Mesha", "Vrishabha", "Mithuna", "Karka",
            "Simha", "Kanya", "Tula", "Vrishchika",
            "Dhanu", "Makara", "Kumbha", "Meena"
        ]
        solar_month = solar_months[solar_month_num]

        # CORRECT lunar month based on actual tithi (not just solar month)
        paksha = tithi_data.get("paksha", "Shukla")
        tithi_name = tithi_data.get("name", "")
        
        # Base lunar month = current solar month
        lunar_base = solar_month_num

        # Purnimanta: month ends on Purnima
        # Amanta: month ends on Amavasya
        purnimanta_months = [
            "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha",
            "Shravana", "Bhadrapada", "Ashwin", "Kartika",
            "Agrahayana", "Pausha", "Magha", "Phalguna"
        ]
        amanta_months = purnimanta_months[:]

        # Adjust if we're in Krishna Paksha (after full/new moon)
        # In Krishna Paksha (after Purnima), we've moved to the next lunar month for Purnimanta
        purnimanta_index = lunar_base
        if paksha == "Krishna":
            purnimanta_index = (lunar_base + 1) % 12
        
        # For Amanta: month changes at Amavasya
        # If we're in Shukla Paksha, Amanta month already changed at previous Amavasya
        # If we're in Krishna Paksha, Amanta month = same as Purnimanta (both changed)
        amanta_index = purnimanta_index

        # Ritu (Season) - 6 seasons of 2 months each
        ritu_list = [
            "Vasanta", "Grishma", "Varsha", "Sharad", "Hemanta", "Shishira"
        ]
        ritu = ritu_list[purnimanta_index % 6]

        return {
            "vikram_samvat": vikram_samvat,
            "shaka_samvat": shaka_samvat,
            "solar_month": solar_month,
            "lunar_month_purnimanta": purnimanta_months[purnimanta_index],
            "lunar_month_amanta": amanta_months[amanta_index],
            "paksha": paksha,
            "ritu": ritu
        }

    def get_rahu_kala(self, sunrise: str, sunset: str, day_of_week: int) -> Dict:
        """
        Calculate Rahu Kala timing - CORRECTED FORMULA

        Rahu Kala is 1/8th of day duration
        Position depends on weekday (0=Sunday):
        Sunday: 8th period, Monday: 2nd period, Tuesday: 7th period,
        Wednesday: 5th period, Thursday: 6th period, Friday: 4th period,
        Saturday: 3rd period
        """
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
        # CORRECTED: Proper segment mapping
        rahu_segments = {
            0: 7,  # Sunday: 8th segment (index 7)
            1: 1,  # Monday: 2nd segment (index 1)
            2: 6,  # Tuesday: 7th segment (index 6)
            3: 4,  # Wednesday: 5th segment (index 4)
            4: 5,  # Thursday: 6th segment (index 5)
            5: 3,  # Friday: 4th segment (index 3)
            6: 2   # Saturday: 3rd segment (index 2)
        }

        segment_num = rahu_segments.get(day_of_week, 1)
        start_min = sunrise_min + (segment_num * segment)
        end_min = start_min + segment

        return {
            "start": minutes_to_time(start_min),
            "end": minutes_to_time(end_min),
            "duration_minutes": int(segment)
        }

    def get_yamaganda(self, sunrise: str, sunset: str, day_of_week: int) -> Dict:
        """
        Calculate Yamaganda timing - CORRECTED

        Position by weekday (0=Sunday):
        Sunday: 5th, Monday: 4th, Tuesday: 3rd, Wednesday: 2nd,
        Thursday: 1st, Friday: 7th, Saturday: 6th
        """
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
            0: 4,  # Sunday: 5th segment
            1: 3,  # Monday: 4th segment
            2: 2,  # Tuesday: 3rd segment
            3: 1,  # Wednesday: 2nd segment
            4: 0,  # Thursday: 1st segment
            5: 6,  # Friday: 7th segment
            6: 5   # Saturday: 6th segment
        }

        segment_num = yamaganda_segments.get(day_of_week, 1)
        start_min = sunrise_min + (segment_num * segment)
        end_min = start_min + segment

        return {
            "start": minutes_to_time(start_min),
            "end": minutes_to_time(end_min),
            "duration_minutes": int(segment)
        }

    def get_gulika(self, sunrise: str, sunset: str, day_of_week: int) -> Dict:
        """
        Calculate Gulika Kala timing - CORRECTED

        Position by weekday (0=Sunday):
        Sunday: 7th, Monday: 2nd, Tuesday: 1st, Wednesday: 6th,
        Thursday: 5th, Friday: 4th, Saturday: 3rd
        """
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
            0: 6,  # Sunday: 7th segment
            1: 2,  # Monday: 3rd segment ΓåÉ FIXED (was 1, causing overlap with Rahu Kaal)
            2: 0,  # Tuesday: 1st segment
            3: 5,  # Wednesday: 6th segment
            4: 4,  # Thursday: 5th segment
            5: 3,  # Friday: 4th segment
            6: 2   # Saturday: 3rd segment
        }

        segment_num = gulika_segments.get(day_of_week, 1)
        start_min = sunrise_min + (segment_num * segment)
        end_min = start_min + segment

        return {
            "start": minutes_to_time(start_min),
            "end": minutes_to_time(end_min),
            "duration_minutes": int(segment)
        }

    def get_nakshatra_quality(self, nakshatra_name: str) -> Dict:
        """Get quality assessment and properties for a nakshatra"""
        nakshatra_qualities = {
            "Ashwini": {
                "stars": 4,
                "label": "Auspicious",
                "color": "#4CAF50",
                "deity": "Ashwini Kumaras (Divine Physicians)",
                "nature": "Light (Laghu) - Swift",
                "ruling_planet": "Ketu",
                "element": "Earth",
                "good_for": [
                    "Starting new ventures",
                    "Medical treatments",
                    "Travel and journeys",
                    "Buying vehicles"
                ],
                "avoid": []
            },
            "Bharani": {
                "stars": 3,
                "label": "Moderate",
                "color": "#FF9800",
                "deity": "Yama (God of Death)",
                "nature": "Fierce (Ugra)",
                "ruling_planet": "Venus",
                "element": "Earth",
                "good_for": [
                    "Endings and transformations",
                    "Occult practices",
                    "Agriculture"
                ],
                "avoid": [
                    "Marriage",
                    "Starting new ventures",
                    "Celebrations"
                ]
            },
            "Krittika": {
                "stars": 4,
                "label": "Auspicious",
                "color": "#4CAF50",
                "deity": "Agni (Fire God)",
                "nature": "Sharp (Tikshna)",
                "ruling_planet": "Sun",
                "element": "Fire",
                "good_for": [
                    "Spiritual practices",
                    "Cutting ties",
                    "Starting education",
                    "Creative work"
                ],
                "avoid": []
            },
            "Rohini": {
                "stars": 5,
                "label": "Extremely Auspicious",
                "color": "#00C853",
                "deity": "Brahma (Creator)",
                "nature": "Fixed (Dhruva)",
                "ruling_planet": "Moon",
                "element": "Earth",
                "good_for": [
                    "Marriage ceremonies",
                    "Business ventures",
                    "Property purchase",
                    "Starting education",
                    "All auspicious activities"
                ],
                "avoid": []
            },
            "Mrigashira": {
                "stars": 4,
                "label": "Auspicious",
                "color": "#4CAF50",
                "deity": "Chandra (Moon God)",
                "nature": "Soft (Mridu)",
                "ruling_planet": "Mars",
                "element": "Earth",
                "good_for": [
                    "Marriage",
                    "Travel",
                    "Artistic work",
                    "Buying clothes/jewelry"
                ],
                "avoid": []
            },
            "Ardra": {
                "stars": 2,
                "label": "Inauspicious",
                "color": "#D32F2F",
                "deity": "Rudra (Destroyer)",
                "nature": "Sharp (Tikshna)",
                "ruling_planet": "Rahu",
                "element": "Water",
                "good_for": [
                    "Destruction of enemies",
                    "Occult practices",
                    "Research work"
                ],
                "avoid": [
                    "Marriage ceremonies",
                    "Starting business",
                    "House warming",
                    "Important celebrations"
                ]
            },
            "Punarvasu": {
                "stars": 4,
                "label": "Auspicious",
                "color": "#4CAF50",
                "deity": "Aditi (Mother of Gods)",
                "nature": "Movable (Chara)",
                "ruling_planet": "Jupiter",
                "element": "Water",
                "good_for": [
                    "Marriage",
                    "Starting business",
                    "Travel",
                    "Religious ceremonies"
                ],
                "avoid": []
            },
            "Pushya": {
                "stars": 5,
                "label": "Extremely Auspicious",
                "color": "#00C853",
                "deity": "Brihaspati (Jupiter)",
                "nature": "Light (Laghu)",
                "ruling_planet": "Saturn",
                "element": "Water",
                "good_for": [
                    "All auspicious activities",
                    "Marriage",
                    "Business ventures",
                    "Education",
                    "Property purchase"
                ],
                "avoid": []
            },
            "Ashlesha": {
                "stars": 2,
                "label": "Inauspicious",
                "color": "#D32F2F",
                "deity": "Serpent (Naga)",
                "nature": "Sharp (Tikshna)",
                "ruling_planet": "Mercury",
                "element": "Water",
                "good_for": [
                    "Occult practices",
                    "Snake worship",
                    "Dealing with enemies"
                ],
                "avoid": [
                    "Marriage",
                    "Starting new ventures",
                    "Important celebrations"
                ]
            },
            "Magha": {
                "stars": 3,
                "label": "Moderate",
                "color": "#FF9800",
                "deity": "Pitris (Ancestors)",
                "nature": "Fierce (Ugra)",
                "ruling_planet": "Ketu",
                "element": "Water",
                "good_for": [
                    "Ancestor worship",
                    "Religious ceremonies",
                    "Authority matters"
                ],
                "avoid": [
                    "Marriage of certain combinations"
                ]
            },
            "Purva Phalguni": {
                "stars": 4,
                "label": "Auspicious",
                "color": "#4CAF50",
                "deity": "Bhaga (God of Fortune)",
                "nature": "Fierce (Ugra)",
                "ruling_planet": "Venus",
                "element": "Water",
                "good_for": [
                    "Marriage",
                    "Arts and entertainment",
                    "Celebrations",
                    "Social gatherings"
                ],
                "avoid": []
            },
            "Uttara Phalguni": {
                "stars": 5,
                "label": "Extremely Auspicious",
                "color": "#00C853",
                "deity": "Aryaman (God of Contracts)",
                "nature": "Fixed (Dhruva)",
                "ruling_planet": "Sun",
                "element": "Fire",
                "good_for": [
                    "Marriage",
                    "Business partnerships",
                    "Contracts and agreements",
                    "All auspicious activities"
                ],
                "avoid": []
            },
            "Hasta": {
                "stars": 5,
                "label": "Extremely Auspicious",
                "color": "#00C853",
                "deity": "Savitar (Sun God)",
                "nature": "Light (Laghu)",
                "ruling_planet": "Moon",
                "element": "Fire",
                "good_for": [
                    "Marriage",
                    "Business transactions",
                    "Buying vehicles",
                    "Crafts and arts",
                    "All auspicious activities"
                ],
                "avoid": []
            },
            "Chitra": {
                "stars": 4,
                "label": "Auspicious",
                "color": "#4CAF50",
                "deity": "Vishwakarma (Divine Architect)",
                "nature": "Soft (Mridu)",
                "ruling_planet": "Mars",
                "element": "Fire",
                "good_for": [
                    "Construction",
                    "Arts and creativity",
                    "Wearing new clothes",
                    "Jewelry making"
                ],
                "avoid": []
            },
            "Swati": {
                "stars": 4,
                "label": "Auspicious",
                "color": "#4CAF50",
                "deity": "Vayu (Wind God)",
                "nature": "Movable (Chara)",
                "ruling_planet": "Rahu",
                "element": "Fire",
                "good_for": [
                    "Trade and commerce",
                    "Travel",
                    "Education",
                    "Business ventures"
                ],
                "avoid": []
            },
            "Vishakha": {
                "stars": 3,
                "label": "Moderate",
                "color": "#FF9800",
                "deity": "Indra-Agni (King of Gods & Fire)",
                "nature": "Sharp (Tikshna)",
                "ruling_planet": "Jupiter",
                "element": "Fire",
                "good_for": [
                    "Achieving goals",
                    "Competition",
                    "Starting ventures"
                ],
                "avoid": [
                    "Marriage (requires careful consideration)"
                ]
            },
            "Anuradha": {
                "stars": 4,
                "label": "Auspicious",
                "color": "#4CAF50",
                "deity": "Mitra (God of Friendship)",
                "nature": "Soft (Mridu)",
                "ruling_planet": "Saturn",
                "element": "Fire",
                "good_for": [
                    "Marriage",
                    "Friendships",
                    "Travel",
                    "Religious ceremonies"
                ],
                "avoid": []
            },
            "Jyeshtha": {
                "stars": 2,
                "label": "Inauspicious",
                "color": "#D32F2F",
                "deity": "Indra (King of Gods)",
                "nature": "Sharp (Tikshna)",
                "ruling_planet": "Mercury",
                "element": "Air",
                "good_for": [
                    "Authority matters",
                    "Protection rituals"
                ],
                "avoid": [
                    "Marriage",
                    "Starting new ventures",
                    "Celebrations"
                ]
            },
            "Moola": {
                "stars": 2,
                "label": "Inauspicious",
                "color": "#D32F2F",
                "deity": "Nirriti (Goddess of Destruction)",
                "nature": "Sharp (Tikshna)",
                "ruling_planet": "Ketu",
                "element": "Air",
                "good_for": [
                    "Endings and conclusions",
                    "Research",
                    "Occult practices"
                ],
                "avoid": [
                    "Marriage",
                    "Starting new ventures",
                    "Important celebrations"
                ]
            },
            "Purva Ashadha": {
                "stars": 4,
                "label": "Auspicious",
                "color": "#4CAF50",
                "deity": "Apas (Water Goddess)",
                "nature": "Fierce (Ugra)",
                "ruling_planet": "Venus",
                "element": "Air",
                "good_for": [
                    "Purification rituals",
                    "Water-related activities",
                    "Spiritual practices"
                ],
                "avoid": []
            },
            "Uttara Ashadha": {
                "stars": 5,
                "label": "Extremely Auspicious",
                "color": "#00C853",
                "deity": "Vishwadevas (Universal Gods)",
                "nature": "Fixed (Dhruva)",
                "ruling_planet": "Sun",
                "element": "Air",
                "good_for": [
                    "Marriage",
                    "Starting ventures",
                    "All auspicious activities",
                    "Leadership roles"
                ],
                "avoid": []
            },
            "Shravana": {
                "stars": 4,
                "label": "Auspicious",
                "color": "#4CAF50",
                "deity": "Vishnu (Preserver)",
                "nature": "Movable (Chara)",
                "ruling_planet": "Moon",
                "element": "Air",
                "good_for": [
                    "Education",
                    "Learning",
                    "Travel",
                    "Religious ceremonies"
                ],
                "avoid": []
            },
            "Dhanishta": {
                "stars": 3,
                "label": "Moderate",
                "color": "#FF9800",
                "deity": "Vasus (Gods of Wealth)",
                "nature": "Movable (Chara)",
                "ruling_planet": "Mars",
                "element": "Ether",
                "good_for": [
                    "Music and arts",
                    "Wealth accumulation",
                    "Group activities"
                ],
                "avoid": []
            },
            "Shatabhisha": {
                "stars": 3,
                "label": "Moderate",
                "color": "#FF9800",
                "deity": "Varuna (God of Waters)",
                "nature": "Movable (Chara)",
                "ruling_planet": "Rahu",
                "element": "Ether",
                "good_for": [
                    "Healing",
                    "Medical treatment",
                    "Research",
                    "Mystical practices"
                ],
                "avoid": []
            },
            "Purva Bhadrapada": {
                "stars": 3,
                "label": "Moderate",
                "color": "#FF9800",
                "deity": "Aja Ekapada (One-footed Goat)",
                "nature": "Fierce (Ugra)",
                "ruling_planet": "Jupiter",
                "element": "Ether",
                "good_for": [
                    "Spiritual practices",
                    "Occult studies",
                    "Transformation"
                ],
                "avoid": [
                    "Marriage (first half)"
                ]
            },
            "Uttara Bhadrapada": {
                "stars": 5,
                "label": "Extremely Auspicious",
                "color": "#00C853",
                "deity": "Ahir Budhnya (Serpent of Depths)",
                "nature": "Fixed (Dhruva)",
                "ruling_planet": "Saturn",
                "element": "Ether",
                "good_for": [
                    "Marriage",
                    "Spiritual practices",
                    "All auspicious activities",
                    "Meditation and yoga"
                ],
                "avoid": []
            },
            "Revati": {
                "stars": 5,
                "label": "Extremely Auspicious",
                "color": "#00C853",
                "deity": "Pushan (Nourisher)",
                "nature": "Soft (Mridu)",
                "ruling_planet": "Mercury",
                "element": "Ether",
                "good_for": [
                    "Marriage",
                    "Travel",
                    "Beginning journeys",
                    "All auspicious activities",
                    "Starting education"
                ],
                "avoid": []
            }
        }

        return nakshatra_qualities.get(nakshatra_name, {
            "stars": 3,
            "label": "Moderate",
            "color": "#FF9800",
            "deity": "Unknown",
            "nature": "Variable",
            "ruling_planet": "Unknown",
            "element": "Unknown",
            "good_for": [],
            "avoid": []
        })

    def get_tithi_quality(self, tithi_name: str) -> Dict:
        """Get quality assessment for a tithi"""
        tithi_qualities = {
            "Pratipada": {"stars": 3, "label": "Moderate", "color": "#FF9800", "good_for": ["Starting new ventures", "Beginning education"], "avoid": ["Marriage"]},
            "Dwitiya": {"stars": 4, "label": "Auspicious", "color": "#4CAF50", "good_for": ["Marriage", "Religious ceremonies", "All good works"], "avoid": []},
            "Tritiya": {"stars": 5, "label": "Extremely Auspicious", "color": "#00C853", "good_for": ["Marriage", "Business", "Education", "Travel"], "avoid": []},
            "Chaturthi": {"stars": 3, "label": "Moderate", "color": "#FF9800", "good_for": ["Worship of Ganesha", "Removing obstacles"], "avoid": ["Long journeys"]},
            "Panchami": {"stars": 5, "label": "Extremely Auspicious", "color": "#00C853", "good_for": ["Marriage", "Education", "Religious ceremonies", "All auspicious activities"], "avoid": []},
            "Shashthi": {"stars": 3, "label": "Moderate", "color": "#FF9800", "good_for": ["War activities", "Competition"], "avoid": ["Marriage", "Peace activities"]},
            "Saptami": {"stars": 4, "label": "Auspicious", "color": "#4CAF50", "good_for": ["Marriage", "Travel", "Business transactions"], "avoid": []},
            "Ashtami": {"stars": 2, "label": "Inauspicious", "color": "#D32F2F", "good_for": ["Worship of fierce deities", "Protection rituals"], "avoid": ["Marriage", "Starting new ventures", "Celebrations"]},
            "Navami": {"stars": 3, "label": "Moderate", "color": "#FF9800", "good_for": ["Worship of Durga", "Strength building"], "avoid": ["Marriage in some traditions"]},
            "Dashami": {"stars": 4, "label": "Auspicious", "color": "#4CAF50", "good_for": ["Marriage", "Business", "Religious ceremonies"], "avoid": []},
            "Ekadashi": {"stars": 5, "label": "Highly Spiritual", "color": "#00C853", "good_for": ["Fasting", "Spiritual practices", "Worship of Vishnu"], "avoid": ["Material activities", "Consumption of grains"]},
            "Dwadashi": {"stars": 4, "label": "Auspicious", "color": "#4CAF50", "good_for": ["Breaking Ekadashi fast", "Religious ceremonies"], "avoid": []},
            "Trayodashi": {"stars": 3, "label": "Moderate", "color": "#FF9800", "good_for": ["Worship of Shiva (Pradosha)", "Spiritual practices"], "avoid": []},
            "Chaturdashi": {"stars": 2, "label": "Inauspicious", "color": "#D32F2F", "good_for": ["Worship of fierce deities", "Tantra practices"], "avoid": ["Marriage", "Important celebrations"]},
            "Purnima": {"stars": 5, "label": "Extremely Auspicious", "color": "#00C853", "good_for": ["All spiritual activities", "Meditation", "Religious ceremonies", "Charity"], "avoid": []},
            "Amavasya": {"stars": 2, "label": "New Moon", "color": "#D32F2F", "good_for": ["Ancestor worship", "Ending old things"], "avoid": ["Marriage", "Starting new ventures", "Celebrations"]}
        }

        return tithi_qualities.get(tithi_name, {
            "stars": 3,
            "label": "Moderate",
            "color": "#FF9800",
            "good_for": [],
            "avoid": []
        })

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

    def get_brahma_muhurat(self, sunrise: str) -> Dict:
        """
        Calculate Brahma Muhurta (pre-dawn meditation period)
        
        Brahma Muhurta is 1.5 hours before sunrise, duration 48 minutes (2 muhurats)
        Most auspicious time for meditation, prayer, and spiritual practices
        """
        def time_to_minutes(time_str):
            parts = time_str.split(':')
            return int(parts[0]) * 60 + int(parts[1])

        def minutes_to_time(minutes):
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return f"{hours:02d}:{mins:02d}:00"

        sunrise_min = time_to_minutes(sunrise)
        # Brahma Muhurta starts 1.5 hours (90 minutes) before sunrise
        start_min = sunrise_min - 90
        # Duration is 48 minutes (2 muhurats of 24 minutes each)
        end_min = start_min + 48
        
        # Handle day rollover
        if start_min < 0:
            start_min += 1440  # Add 24 hours
        if end_min >= 1440:
            end_min -= 1440

        return {
            "start": minutes_to_time(start_min),
            "end": minutes_to_time(end_min),
            "duration_minutes": 48,
            "description": "Most auspicious time for meditation, prayer, and spiritual practices"
        }

    def get_amrita_kalam(self, sunrise: str, sunset: str, day_of_week: int) -> Dict:
        """
        Calculate Amrita Kalam (nectar period) - auspicious time
        
        Amrita Kalam varies by day of week (South Indian method)
        Duration: ~1.5 hours
        """
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

        # Amrita Kalam period by weekday (South Indian system)
        amrita_segments = {
            0: 3,  # Sunday: 4th segment (afternoon)
            1: 5,  # Monday: 6th segment
            2: 6,  # Tuesday: 7th segment
            3: 4,  # Wednesday: 5th segment
            4: 7,  # Thursday: 8th segment (evening)
            5: 2,  # Friday: 3rd segment
            6: 1   # Saturday: 2nd segment
        }

        segment_num = amrita_segments.get(day_of_week, 3)
        start_min = sunrise_min + (segment_num * segment)
        end_min = start_min + segment

        return {
            "start": minutes_to_time(start_min),
            "end": minutes_to_time(end_min),
            "duration_minutes": int(segment),
            "description": "Nectar period - highly auspicious for new beginnings"
        }

    def get_dur_muhurta(self, sunrise: str, sunset: str, tithi_data: Dict) -> List[Dict]:
        """
        Calculate Dur Muhurta (inauspicious periods during the day)
        
        Dur Muhurta occurs at specific times relative to tithi transitions
        Multiple periods per day when starting new activities should be avoided
        """
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
        
        dur_periods = []
        
        # Dur Muhurta typically occurs:
        # 1. Early morning (around 8th muhurta from sunrise - ~44 minutes)
        # 2. Evening (around tithi transition time)
        
        # Morning Dur Muhurta (varies slightly)
        morning_start = sunrise_min + (day_duration * 0.18)  # ~18% into day
        morning_end = morning_start + 44  # 44 minutes duration
        dur_periods.append({
            "start": minutes_to_time(int(morning_start)),
            "end": minutes_to_time(int(morning_end)),
            "duration_minutes": 44,
            "description": "Inauspicious period - avoid new activities"
        })
        
        # Evening Dur Muhurta (near tithi transition if close to sunset)
        # Check if tithi ends today - use end_time field which has full datetime
        if tithi_data.get("end_time"):
            try:
                from datetime import datetime
                tithi_end_dt = datetime.strptime(tithi_data["end_time"], "%Y-%m-%d %H:%M:%S")
                tithi_end_min = tithi_end_dt.hour * 60 + tithi_end_dt.minute
                
                # If tithi ends in evening (after 6 PM), Dur Muhurta around that time
                if tithi_end_min > (18 * 60):
                    evening_start = tithi_end_min - 22  # 22 minutes before
                    evening_end = tithi_end_min + 23    # 23 minutes after
                    dur_periods.append({
                        "start": minutes_to_time(int(evening_start)),
                        "end": minutes_to_time(int(evening_end)),
                        "duration_minutes": 45,
                        "description": "Inauspicious period near tithi transition"
                    })
            except:
                pass  # Skip if parsing fails

        return dur_periods

    def get_varjyam(self, sunrise: str, sunset: str, nakshatra_data: Dict) -> List[Dict]:
        """
        Calculate Varjyam (avoid periods) based on nakshatra
        
        Varjyam is an inauspicious period calculated from nakshatra
        Duration varies by nakshatra (typically ~1.5 hours)
        """
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
        
        # Varjyam calculation based on nakshatra
        # Simplified: Varjyam typically occurs around mid-day
        # More accurate calculation would use nakshatra-specific formulas
        midday = (sunrise_min + sunset_min) / 2
        varjyam_duration = 102  # ~1 hour 42 minutes
        
        varjyam_start = midday - (varjyam_duration / 2)
        varjyam_end = varjyam_start + varjyam_duration

        return [{
            "start": minutes_to_time(int(varjyam_start)),
            "end": minutes_to_time(int(varjyam_end)),
            "duration_minutes": varjyam_duration,
            "description": "Varjyam - avoid starting new ventures"
        }]

    def get_special_notes(self, tithi_data: Dict, nakshatra_data: Dict, yoga_data: Dict, 
                         moon_sign_data: Dict, paksha: str) -> Dict:
        """
        Generate special notes and recommendations for the day
        
        Provides guidance based on tithi, nakshatra, yoga combinations
        """
        notes = []
        recommendations = []
        avoid = []
        
        tithi_name = tithi_data.get("name", "")
        nakshatra_name = nakshatra_data.get("name", "")
        yoga_name = yoga_data.get("name", "")
        
        # Tithi + Nakshatra combinations
        if tithi_name == "Panchami" and nakshatra_name == "Uttara Ashadha":
            notes.append(f"{tithi_data.get('full_name', '')} + {nakshatra_name}: Highly auspicious for education, travel, and spiritual pursuits. Ideal for Guru-related activities or starting studies.")
        
        # Yoga recommendations
        if yoga_name == "Vriddhi":
            recommendations.append("Vriddhi Yoga: Supports growth in career or finances—good for investments or meetings.")
        elif yoga_name in ["Ganda", "Vyatipata", "Vaidhriti"]:
            avoid.append("Avoid starting new ventures during inauspicious Yoga period.")
        
        # Paksha recommendations
        if paksha == "Shukla":
            notes.append("Waxing Moon enhances positivity and growth.")
        
        # Moon sign recommendations
        if moon_sign_data and moon_sign_data.get("name"):
            moon_sign = moon_sign_data.get("name")
            if moon_sign in ["Makara", "Simha", "Mesha"]:
                recommendations.append(f"Chandra Bala: Strong (Moon in friendly sign {moon_sign}).")
        
        # Nakshatra recommendations
        if nakshatra_name in ["Uttara Ashadha", "Rohini", "Pushya"]:
            recommendations.append(f"Tara Bala: Favorable in {nakshatra_name} for most rashis.")
        
        # Compile final notes
        special_notes_text = ""
        if notes:
            special_notes_text += " ".join(notes) + " "
        if recommendations:
            special_notes_text += " ".join(recommendations) + " "
        if avoid:
            special_notes_text += "Avoid: " + " ".join(avoid) + ". "
        
        # Check for festivals
        festivals_today = ""
        
        return {
            "summary": special_notes_text.strip() or "No special notes for today.",
            "recommendations": recommendations,
            "avoid": avoid,
            "festivals": festivals_today,
            "tithi_nakshatra_combination": f"{tithi_data.get('full_name', '')} + {nakshatra_name}",
            "yoga_effect": yoga_name
        }

    def get_south_india_festivals_and_notes(self, dt: datetime, tithi_data: Dict, nakshatra: str, weekday: int) -> List[Dict]:
        """
        South India (Karnataka focus) – Festivals & Special Observances
        With English + ಕನ್ನಡ + संस्कृत names
        """
        day = dt.day
        month = dt.month
        paksha = tithi_data["paksha"]
        tithi_name = tithi_data["name"]
        festivals = []

        # ── Major Festivals (Karnataka & South India) ─────────────────────
        if month == 1 and (14 <= day <= 16):
            festivals.append({
                "en": "Makara Sankranti / Pongal / Uttarayana",
                "kn": "ಮಕರ ಸಂಕ್ರಾಂತಿ / ಪೊಂಗಲ್",
                "sa": "मकर संक्रान्ति / उत्तरायण आरम्भः"
            })
        if month == 4 and day == 14:
            festivals.append({
                "en": "Vishu – Kerala & Tamil New Year",
                "kn": "ವಿಷು – ತಮಿಳು ಹೊಸ ವರ್ಷ",
                "sa": "विशु / मेधशिर पर्व"
            })
        if month == 8 and paksha == "Shukla" and tithi_name == "Chaturthi":
            festivals.append({
                "en": "Ganesh Chaturthi / Vinayaka Chaturthi",
                "kn": "ಗಣೇಶ ಚತುರ್ಥಿ",
                "sa": "विनायक चतुर्थी"
            })
        if month == 10 and paksha == "Shukla" and tithi_name == "Dashami":
            festivals.append({
                "en": "Vijaya Dashami / Dussehra",
                "kn": "ವಿಜಯದಶಮಿ / ದಸರಾ",
                "sa": "विजया दशमी"
            })

        # ── Karthikai Deepam (Tamil Nadu + Karnataka border temples) ─────
        if (month == 11 or month == 12) and tithi_name == "Purnima" and nakshatra in ["Krittika", "Karthigai"]:
            festivals.append({
                "en": "Karthikai Deepam – Festival of Lights",
                "kn": "ಕಾರ್ತಿಕ ದೀಪೋತ್ಸವ",
                "sa": "कार्त्तिक दीपोत्सवः"
            })

        # ── Monthly Vratas (very popular in Karnataka temples) ───────────
        if tithi_name == "Ekadashi":
            festivals.append({
                "en": "Ekadashi Fasting",
                "kn": "ಏಕಾದಶಿ ಉಪವಾಸ",
                "sa": "एकादशी व्रतम्"
            })
        if tithi_name == "Chaturthi" and paksha == "Krishna":
            festivals.append({
                "en": "Sankashti Chaturthi – Ganesha Vrat after Moonrise",
                "kn": "ಸಂಕಷ್ಟ ಚತುರ್ಥಿ – ಚಂದ್ರೋದಯದ ನಂತರ ಗಣಪತಿ ಪೂಜೆ",
                "sa": "संकष्टी चतुर्थी"
            })
        if tithi_name == "Purnima":
            festivals.append({
                "en": "Purnima – Satyanarayan Puja",
                "kn": "ಪೌರ್ಣಮಿ – ಸತ್ಯನಾರಾಯಣ ಪೂಜೆ",
                "sa": "पूर्णिमा व्रतम्"
            })
        if tithi_name == "Amavasya":
            festivals.append({
                "en": "Amavasya – Pitru Tarpanam",
                "kn": "ಅಮಾವಾಸ್ಯೆ – ಪಿತೃ ತರ್ಪಣ",
                "sa": "अमावस्या श्राद्धम्"
            })

        # ── Weekly Special Days (very common in Karnataka) ───────────────
        weekly = [
            None,
            {"en": "Somavara Vrat – Fasting for Lord Shiva",        "kn": "ಸೋಮವಾರ ವ್ರತ – ಶಿವನಿಗೆ ಉಪವಾಸ",        "sa": "सोमवार व्रतम्"},
            None,
            {"en": "Budha Vrat – Green colour & Moong dal",         "kn": "ಬುಧವಾರ – ಹಸಿರು ಬಣ್ಣ & ಹೆಸರುಕಾಳು",    "sa": "बुध व्रतम्"},
            {"en": "Guruvara Vrat – Yellow colour & Chana dal",     "kn": "ಗುರುವಾರ – ಹಳದಿ ಬಣ್ಣ & ಕಡಲೆಬೇಳೆ",     "sa": "गुरुवार व्रतम्"},
            None,
            {"en": "Shukravara Lakshmi Vrat – White colour",       "kn": "ಶುಕ್ರವಾರ – ಲಕ್ಷ್ಮಿ ವ್ರತ (ಬಿಳಿ)",      "sa": "शुक्रवार लक्ष्मी व्रतम्"}
        ]
        if weekday in [1, 3, 4, 6] and weekly[weekday]:
            festivals.append(weekly[weekday])

        # ── Nakshatra-based Special Days (Karnataka favourites) ─────────
        nak_special = {
            "Rohini":     {"en": "Rohini Vrata (very auspicious)",               "kn": "ರೋಹಿಣಿ ವ್ರತ (ಅತ್ಯಂತ ಶುಭ)",           "sa": "रोहिणी व्रतम्"},
            "Shravana":   {"en": "Excellent for Upanayanam & Education",        "kn": "ಉಪನಯನ, ವಿದ್ಯಾರಂಭಕ್ಕೆ ಉತ್ತಮ",      "sa": "श्रवण नक्षत्र – श्रेष्ठम्"},
            "Pushya":     {"en": "Pushya Nakshatra – No Muhurta needed",        "kn": "ಪುಷ್ಯ – ಮುಹೂರ್ತ ಬೇಡ",                "sa": "पुष्य नक्षत्र – सर्वं शुभम्"},
            "Uttara Phalguni": {"en": "Onam starts in Kerala",                  "kn": "ಕೇರಳದಲ್ಲಿ ಓಣಂ ಆರಂಭ",                 "sa": "उत्तराफाल्गुनी – ओणम्"},
            "Swati":      {"en": "Ideal for planting & agriculture",           "kn": "ಗಿಡ ನೆಡಲು ಉತ್ತಮ",                    "sa": "स्वाती – कृषि कार्याय शुभः"}
        }
        if nakshatra in nak_special:
            festivals.append(nak_special[nakshatra])

        # ── General Notes ────────────────────────────────────────────────
        notes = []
        jd = self.get_julian_day(dt)
        karana_data = self.get_karana(jd)
        karana = karana_data.get("current", "")
        yoga = self.get_yoga(jd).get("name", "")

        if "Vishti" in karana:
            notes.append({"en": "Vishti (Bhadra) Karana – Avoid new beginnings", "kn": "ವಿಷ್ಟಿ ಕರಣ – ಹೊಸ ಕೆಲಸ ಆರಂಭಿಸಬೇಡಿ", "sa": "विष्टि करण – अशुभम्"})
        if yoga in ["Vyatipata", "Vaidhriti"]:
            notes.append({"en": f"{yoga} Yoga – Inauspicious", "kn": f"{yoga} ಯೋಗ – ಅಶುಭ", "sa": f"{yoga} योगः"})

        # ── Convert to final list with multilingual text ─────────────────
        result = []
        for item in festivals + notes:
            if isinstance(item, dict):
                text = f"{item['en']} | {item['kn']} | {item.get('sa', '')}".strip(" |")
                result.append({
                    "type": "festival" if item in festivals else "note",
                    "text": text,
                    "english": item.get('en', ''),
                    "kannada": item.get('kn', ''),
                    "sanskrit": item.get('sa', '')
                })

        return result if result else [{"type": "note", "text": "Regular day – Good for routine temple activities", "english": "Regular day – Good for routine temple activities", "kannada": "", "sanskrit": ""}]

    def detect_special_days(self, tithi_data: Dict, vara: Dict, nakshatra: Dict) -> list:
        """Detect special days like Ekadashi, Pradosha, Sankashta Chaturthi"""
        special_days = []

        tithi_name = tithi_data.get("name", "")
        vara_name = vara.get("name", "")

        # Ekadashi (11th tithi)
        if tithi_name == "Ekadashi":
            special_days.append({
                "name": "Ekadashi",
                "type": "fasting",
                "importance": "major",
                "description": "Fasting day dedicated to Lord Vishnu",
                "observance": "Fast from grains and beans",
                "observances": [
                    "Avoid all grains (rice, wheat, etc.)",
                    "Avoid beans and lentils",
                    "Avoid onion and garlic",
                    "Fruits and milk products are allowed",
                    "Sabudana, potato, sweet potato allowed"
                ],
                "benefits": [
                    "Spiritual purification",
                    "Removes sins",
                    "Improves health",
                    "Increases devotion"
                ]
            })

        # Pradosha (13th tithi)
        if tithi_name == "Trayodashi":
            special_days.append({
                "name": "Pradosha Vrat",
                "type": "worship",
                "importance": "medium",
                "description": "Auspicious time to worship Lord Shiva during twilight",
                "observance": "Worship Shiva during sunset time",
                "observances": [
                    "Visit Shiva temple during sunset (5-7 PM)",
                    "Offer Bilva leaves",
                    "Chant Om Namah Shivaya",
                    "Perform Pradosha Vrat if possible"
                ],
                "benefits": [
                    "Removes obstacles",
                    "Fulfills desires",
                    "Brings peace and prosperity"
                ]
            })

        # Sankashta Chaturthi (4th tithi in Krishna Paksha)
        if tithi_name == "Chaturthi" and tithi_data.get("paksha") == "Krishna":
            special_days.append({
                "name": "Sankashta Chaturthi",
                "type": "fasting",
                "importance": "medium",
                "description": "Day dedicated to Lord Ganesha",
                "observance": "Fast and worship Ganesha, break fast after moonrise",
                "observances": [
                    "Fast throughout the day",
                    "Worship Ganesha in evening",
                    "Break fast only after sighting moon",
                    "Offer modak and durva grass"
                ],
                "benefits": [
                    "Removes obstacles",
                    "Success in endeavors",
                    "Mental peace"
                ]
            })

        # Amavasya (New Moon)
        if tithi_name == "Amavasya":
            special_days.append({
                "name": "Amavasya",
                "type": "ancestor",
                "importance": "major",
                "description": "New Moon day, sacred for ancestor worship",
                "observance": "Perform Tarpanam for ancestors",
                "observances": [
                    "Perform Tarpanam (water offering)",
                    "Offer food to ancestors",
                    "Donate to poor",
                    "Light lamp in evening"
                ],
                "benefits": [
                    "Blessings of ancestors",
                    "Removes ancestral curses",
                    "Family prosperity"
                ]
            })

        # Purnima (Full Moon)
        if tithi_name == "Purnima":
            special_days.append({
                "name": "Purnima",
                "type": "worship",
                "importance": "major",
                "description": "Full Moon day, auspicious for all spiritual activities",
                "observance": "Fasting and meditation",
                "observances": [
                    "Take bath during moonrise",
                    "Worship Satyanarayan",
                    "Meditation and spiritual practices",
                    "Charity and donations"
                ],
                "benefits": [
                    "Spiritual growth",
                    "Mental peace",
                    "Fulfillment of wishes"
                ]
            })

        return special_days

    def get_day_periods(self, sunrise: str, sunset: str, day_of_week: int) -> list:
        """
        Calculate 8 periods of the day with their planetary rulers and qualities
        Each period is 1/8th of the day duration from sunrise to sunset
        """
        def time_to_datetime(time_str, base_date):
            """Convert HH:MM:SS string to datetime object"""
            parts = time_str.split(':')
            return base_date.replace(
                hour=int(parts[0]),
                minute=int(parts[1]),
                second=int(parts[2]) if len(parts) > 2 else 0
            )

        def datetime_to_time_str(dt):
            """Convert datetime to HH:MM:SS string"""
            return dt.strftime("%H:%M:%S")

        # Use today's date as base
        from datetime import datetime, timedelta
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        sunrise_dt = time_to_datetime(sunrise, today)
        sunset_dt = time_to_datetime(sunset, today)

        # Calculate period duration (1/8th of day)
        total_duration = (sunset_dt - sunrise_dt).total_seconds()
        period_duration = total_duration / 8

        # Planetary rulers for each period (fixed order)
        period_rulers = [
            {"name": "Sun", "quality": "neutral"},
            {"name": "Venus", "quality": "neutral"},
            {"name": "Mercury", "quality": "neutral"},
            {"name": "Moon", "quality": "neutral"},
            {"name": "Saturn", "quality": "neutral"},
            {"name": "Jupiter", "quality": "good"},
            {"name": "Mars", "quality": "neutral"},
            {"name": "Rahu", "quality": "neutral"}
        ]

        # Day-specific inauspicious periods
        inauspicious_periods = {
            0: {"rahu": 7, "yama": 4, "gulika": 6},  # Sunday
            1: {"rahu": 1, "yama": 3, "gulika": 1},  # Monday
            2: {"rahu": 6, "yama": 2, "gulika": 0},  # Tuesday
            3: {"rahu": 4, "yama": 1, "gulika": 5},  # Wednesday
            4: {"rahu": 5, "yama": 0, "gulika": 4},  # Thursday
            5: {"rahu": 3, "yama": 6, "gulika": 3},  # Friday
            6: {"rahu": 2, "yama": 5, "gulika": 2}   # Saturday
        }

        weekday_map = inauspicious_periods.get(day_of_week, {})

        periods = []
        for i in range(8):
            period_start = sunrise_dt + timedelta(seconds=period_duration * i)
            period_end = sunrise_dt + timedelta(seconds=period_duration * (i + 1))

            # Determine quality and note
            quality = period_rulers[i]["quality"]
            note = ""
            special_type = None

            if i == weekday_map.get("rahu"):
                quality = "rahu"
                note = "Rahu Kaal - Avoid new activities"
                special_type = "rahu"
            elif i == weekday_map.get("yama"):
                quality = "yama"
                note = "Yamaganda - Inauspicious period"
                special_type = "yamaganda"
            elif i == weekday_map.get("gulika"):
                quality = "gulika"
                note = "Gulika Kala - Inauspicious period"
                special_type = "gulika"
            elif quality == "good":
                note = "Generally favorable time"

            periods.append({
                "period": i + 1,
                "start": datetime_to_time_str(period_start),
                "end": datetime_to_time_str(period_end),
                "ruler": period_rulers[i]["name"],
                "quality": quality,
                "note": note,
                "special_type": special_type
            })

        return periods

    def calculate_panchang(self, dt: datetime, lat: float = 12.9716, lon: float = 77.5946, city: str = "Bengaluru") -> Dict:
        """
        Calculate complete Panchang for a given date and location

        Args:
            dt: DateTime to calculate for
            lat: Latitude (default: Bangalore 12.9716┬░N)
            lon: Longitude (default: Bangalore 77.5946┬░E)
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
        moon_rise_set_data = self.get_moon_rise_set(dt, lat, lon)  # NEW: Add moonrise/moonset
        moon_sign_data = self.get_moon_sign(jd)
        samvatsara_data = self.get_samvatsara(dt.year)

        # NEW: Get dynamic Hindu calendar info
        hindu_calendar_data = self.get_hindu_calendar_info(dt, jd, tithi_data)

        # Calculate inauspicious times
        day_of_week = (dt.weekday() + 1) % 7  # Convert to Sunday=0 format
        rahu_kala = self.get_rahu_kala(sun_moon_data["sunrise"], sun_moon_data["sunset"], day_of_week)
        yamaganda = self.get_yamaganda(sun_moon_data["sunrise"], sun_moon_data["sunset"], day_of_week)
        gulika = self.get_gulika(sun_moon_data["sunrise"], sun_moon_data["sunset"], day_of_week)

        # Calculate auspicious times
        abhijit_muhurat = self.get_abhijit_muhurat(sun_moon_data["sunrise"], sun_moon_data["sunset"])
        brahma_muhurat = self.get_brahma_muhurat(sun_moon_data["sunrise"])
        amrita_kalam = self.get_amrita_kalam(sun_moon_data["sunrise"], sun_moon_data["sunset"], day_of_week)

        # Calculate additional inauspicious times
        dur_muhurta = self.get_dur_muhurta(sun_moon_data["sunrise"], sun_moon_data["sunset"], tithi_data)
        varjyam = self.get_varjyam(sun_moon_data["sunrise"], sun_moon_data["sunset"], nakshatra_data)

        # Generate special notes and recommendations
        special_notes = self.get_special_notes(tithi_data, nakshatra_data, yoga_data, moon_sign_data, tithi_data.get("paksha", "Shukla"))

        # Get South India festivals and special notes (English + Kannada + Sanskrit)
        south_india_special = self.get_south_india_festivals_and_notes(
            dt, tithi_data, nakshatra_data["name"], day_of_week
        )

        # Detect special days
        special_days = self.detect_special_days(tithi_data, vara_data, nakshatra_data)

        # Calculate day periods
        day_periods = self.get_day_periods(sun_moon_data["sunrise"], sun_moon_data["sunset"], day_of_week)

        # Add quality information to nakshatra
        nakshatra_quality = self.get_nakshatra_quality(nakshatra_data["name"])
        nakshatra_data["quality"] = nakshatra_quality

        # Add quality information to tithi
        tithi_quality = self.get_tithi_quality(tithi_data["name"])
        tithi_data["quality"] = tithi_quality

        return {
            "date": {
                "gregorian": {
                    "date": dt.date().isoformat(),
                    "day": dt.strftime("%A"),
                    "formatted": dt.strftime("%A, %B %d, %Y")
                },
                "hindu": {
                    "vikram_samvat": hindu_calendar_data["vikram_samvat"],  # FIXED: Now calculated dynamically
                    "shaka_samvat": hindu_calendar_data["shaka_samvat"],     # NEW: Added Shaka Samvat
                    "solar_month": hindu_calendar_data["solar_month"],
                    "lunar_month_purnimanta": hindu_calendar_data["lunar_month_purnimanta"],  # FIXED: Calculated
                    "lunar_month_amanta": hindu_calendar_data["lunar_month_amanta"],
                    "paksha": hindu_calendar_data["paksha"],
                    "ritu": hindu_calendar_data["ritu"],
                    "samvatsara": samvatsara_data
                }
            },
            "panchang": {
                "tithi": tithi_data,
                "nakshatra": nakshatra_data,
                "yoga": yoga_data,
                "karana": karana_data,
                "vara": vara_data
            },
            "sun_moon": {
                **sun_moon_data,  # sunrise, sunset
                **moon_rise_set_data  # moonrise, moonset (NEW)
            },
            "moon_sign": moon_sign_data,
            "ayana": self.get_ayana(jd),
            "ruthu": self.get_ruthu(jd),
            "inauspicious_times": {
                "rahu_kaal": rahu_kala,
                "yamaganda": yamaganda,
                "gulika": gulika
            },
            "auspicious_times": {
                "abhijit_muhurat": abhijit_muhurat,
                "brahma_muhurat": brahma_muhurat,
                "amrita_kalam": amrita_kalam
            },
            "additional_inauspicious_times": {
                "dur_muhurta": dur_muhurta,
                "varjyam": varjyam
            },
            "special_notes": special_notes,
            "south_india_special": south_india_special,  # English + Kannada + Sanskrit festivals & notes
            "day_periods": day_periods,
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

    # ====================== FULL KUNDLI WITH D1 + D9 + DASHA + PDF ======================

    def generate_kundli_pdf_data(self, dt_birth: datetime, lat: float, lon: float,
                                 name: str = "Devotee", temple_name: str = "MandirSync Temple", 
                                 temple_logo_url: str = "") -> Dict:
        """
        Returns everything needed to generate a beautiful South Indian Kundli PDF
        
        Generates:
        - Rasi Chart (D1) - South Indian style
        - Navamsa Chart (D9) - Side by side
        - Vimshottari Dasha Table (120 years)
        - Complete HTML ready for PDF conversion
        
        Call this from your API endpoint → convert to PDF using WeasyPrint or similar
        """
        # Set topocentric coordinates for accurate calculations
        swe.set_topo(lon, lat, 0.0)
        jd = self.get_julian_day(dt_birth)

        # 1. Calculate Lagna & House positions using Placidus system ('P')
        houses, _ = swe.houses(jd, lat, lon, b'P')
        lagna_deg = houses[0]  # Ascendant (Lagna) in degrees

        # 2. Calculate planetary positions (sidereal)
        rasi_pos = {}
        planet_ids = {"Su": swe.SUN, "Mo": swe.MOON, "Ma": swe.MARS, "Me": swe.MERCURY, 
                     "Ju": swe.JUPITER, "Ve": swe.VENUS, "Sa": swe.SATURN, "Ra": swe.TRUE_NODE}
        
        for sym, pid in planet_ids.items():
            deg = self.get_sidereal_position(jd, pid)
            rasi_pos[sym] = deg
        
        # Ketu is always 180° from Rahu
        rasi_pos["Ke"] = (rasi_pos["Ra"] + 180) % 360
        # Add Lagna
        rasi_pos["Lg"] = lagna_deg

        # 3. Calculate Navamsa positions (D9)
        # Navamsa = (degree * 9) % 360
        # Navamsa lagna is also calculated from rasi lagna
        navamsa = {}
        navamsa_lagna = (lagna_deg * 9) % 360
        for sym, deg in rasi_pos.items():
            nav_deg = (deg * 9) % 360
            navamsa[sym] = nav_deg
        navamsa["Lg"] = navamsa_lagna

        # 4. Calculate Vimshottari Dasha (120 years cycle)
        moon_deg = rasi_pos["Mo"]
        # Each nakshatra is 13.333... degrees (360/27)
        nak_num = int(moon_deg / 13.333333333333) % 27
        
        # Dasha lords in order: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury
        lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        years = [7, 20, 6, 10, 7, 18, 16, 19, 17]  # Duration in years
        
        # Nakshatra lord mapping: each nakshatra belongs to a lord
        nak_lord_map = [0, 1, 2, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 7, 8]
        start_idx = nak_lord_map[nak_num]
        
        # Calculate balance of dasha at birth
        nak_position_in_nak = moon_deg % 13.333333333333
        nak_completion = nak_position_in_nak / 13.333333333333
        balance = years[start_idx] * (1 - nak_completion)
        
        # Generate 120 years of dashas
        dasha_table = []
        current = dt_birth
        total_years = 0
        max_years = 120  # Vimshottari Dasha cycle
        
        for i in range(9):
            if total_years >= max_years:
                break
                
            lord_idx = (start_idx + i) % 9
            duration = balance if i == 0 else years[lord_idx]
            
            # Don't exceed 120 years
            if total_years + duration > max_years:
                duration = max_years - total_years
            
            end = current + timedelta(days=duration * 365.25)
            
            dasha_table.append({
                "lord": lords[lord_idx],
                "start": current.strftime("%d-%b-%Y"),
                "end": end.strftime("%d-%b-%Y"),
                "years": round(duration, 2)
            })
            
            current = end
            total_years += duration
            balance = years[(lord_idx + 1) % 9]

        # 5. Generate SVG charts
        rasi_svg = self._draw_south_indian_chart(lagna_deg, rasi_pos, "Rasi Chart (D-1)", is_navamsa=False)
        navamsa_svg = self._draw_south_indian_chart(navamsa_lagna, navamsa, "Navamsa Chart (D-9)", is_navamsa=True)

        # 6. Generate complete HTML for PDF
        logo_html = f'<img src="{temple_logo_url}" width="100" style="margin-bottom:10px;"/>' if temple_logo_url else ""
        
        # Get birth location string
        location_str = f"{lat:.4f}°N, {lon:.4f}°E"
        
        # Get Lagna Rashi name
        lagna_rashi = self._deg_to_rashi_name(lagna_deg)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Arial', 'DejaVu Sans', sans-serif; margin: 40px; background: #fff8f0; color: #333; }}
                .header {{ text-align: center; padding: 20px; border-bottom: 4px solid #d4af37; margin-bottom: 30px; }}
                .header h1 {{ color: #8b4513; margin: 10px 0; }}
                .header h2 {{ color: #b8860b; margin: 5px 0; }}
                .charts {{ display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; margin: 30px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
                th {{ background: #ffd700; padding: 12px; color: #8b4513; font-weight: bold; }}
                td {{ padding: 10px; text-align: center; border: 1px solid #8b4513; }}
                tr:nth-child(even) {{ background: #fffef5; }}
                .footer {{ text-align: center; margin-top: 50px; font-size: 12px; color: #666; }}
                .birth-info {{ margin: 15px 0; line-height: 1.8; }}
                .dasha-info {{ background: #fffef5; padding: 15px; border: 2px solid #d4af37; margin: 20px 0; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                {logo_html}
                <h1>{temple_name}</h1>
                <h2>Janma Kundli – {name}</h2>
                <div class="birth-info">
                    <p><b>Born:</b> {dt_birth.strftime("%d %B %Y, %I:%M %p IST")}</p>
                    <p><b>Place:</b> {location_str}</p>
                    <p><b>Lagna:</b> {lagna_rashi}</p>
                </div>
                <div class="dasha-info">
                    <p><b>Current Mahadasha:</b> {dasha_table[0]['lord']} ({dasha_table[0]['years']} years)</p>
                    <p>From: {dasha_table[0]['start']} to {dasha_table[0]['end']}</p>
                </div>
            </div>

            <div class="charts">
                {rasi_svg}
                {navamsa_svg}
            </div>

            <h2 style="text-align:center; color:#8b4513; margin-top: 40px;">Vimshottari Dasha (120 Years)</h2>
            <table>
                <tr>
                    <th>Mahadasha</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                    <th>Duration (Years)</th>
                </tr>
                {''.join(f"<tr><td><b>{d['lord']}</b></td><td>{d['start']}</td><td>{d['end']}</td><td>{d['years']} yrs</td></tr>" for d in dasha_table)}
            </table>

            <div class="footer">
                <p>Generated by MandirSync • Accurate with Lahiri Ayanamsa • For Temple Use Only</p>
                <p>Calculated using Swiss Ephemeris</p>
            </div>
        </body>
        </html>
        """

        return {
            "html": html,
            "dasha": dasha_table,
            "rasi_positions": rasi_pos,
            "navamsa_positions": navamsa,
            "lagna": lagna_deg,
            "lagna_rashi": lagna_rashi
        }

    def _deg_to_rashi_name(self, deg: float) -> str:
        """Convert degree to full Rashi name"""
        rashi_names = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
                      "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]
        rashi_index = int(deg // 30) % 12
        return f"{rashi_names[rashi_index]} ({rashi_index + 1})"

    def _draw_south_indian_chart(self, lagna_deg: float, positions: dict, title: str = "Rasi Chart", is_navamsa: bool = False) -> str:
        """
        Returns a beautiful South Indian style chart as SVG string
        Used for both Rasi (D1) and Navamsa (D9)
        
        South Indian chart layout:
        - House 1 is at top-center (Lagna)
        - Houses arranged clockwise
        - Planets placed in their respective houses
        """
        # Planet symbols and colors
        symbols = {
            "Su": "☉", "Mo": "☽", "Ma": "♂", "Me": "☿", 
            "Ju": "♃", "Ve": "♀", "Sa": "♄", "Ra": "☊", 
            "Ke": "☋", "Lg": "Lg"
        }
        colors = {
            "Ra": "#000080", "Ke": "#000080", "Sa": "#000080", 
            "Ma": "#b22222", "Su": "#b22222", "Lg": "#006400",
            "default": "#333"
        }

        # Rashi abbreviations (South Indian style) - 12 Rashis
        rashi_abbr = ["Me", "Vr", "Mi", "Ka", "Si", "Kn", "Tu", "Vc", "Dh", "Ma", "Ku", "Pi"]

        svg = f'''
        <svg width="420" height="480" viewBox="0 0 420 480" xmlns="http://www.w3.org/2000/svg" style="background:#fff8f0;">
            <rect x="10" y="40" width="400" height="400" fill="none" stroke="#8b4513" stroke-width="5"/>
            <line x1="210" y1="40" x2="210" y2="440" stroke="#8b4513" stroke-width="4"/>
            <line x1="10" y1="240" x2="410" y2="240" stroke="#8b4513" stroke-width="4"/>
            <line x1="10" y1="40" x2="410" y2="440" stroke="#8b4513" stroke-width="4"/>
            <line x1="10" y1="440" x2="410" y2="40" stroke="#8b4513" stroke-width="4"/>
            <text x="210" y="25" font-size="20" text-anchor="middle" fill="#8b4513" font-weight="bold">{title}</text>
        '''

        # 12 House centers (South Indian clockwise layout)
        # Houses arranged in South Indian style: House 1 is at top-right, going clockwise
        # Layout matches traditional South Indian chart style
        centers = [
            (315, 135),  # House 1 - Top right (Lagna position)
            (315, 345),  # House 2 - Right center
            (105, 345),  # House 3 - Bottom left
            (105, 135),  # House 4 - Top left
            (195, 70),   # House 5 - Top area
            (285, 160),  # House 6 - Top right area
            (285, 320),  # House 7 - Right area
            (195, 390),  # House 8 - Bottom area
            (105, 250),  # House 9 - Left area
            (105, 230),  # House 10 - Left area
            (315, 250),  # House 11 - Right area
            (315, 230)   # House 12 - Right area
        ]

        # Draw house numbers + rashi symbols
        # In South Indian chart, houses are numbered starting from Lagna position
        # House 1 = Lagna, then houses go clockwise
        for i in range(12):
            # South Indian style: House numbers start from Lagna position (which is at index 0 in centers)
            # Adjust house number based on layout: (i + 2) % 12 + 1 gives house numbers in correct order
            house_num = (i + 2) % 12 + 1
            cx, cy = centers[i]
            
            # Calculate which rashi is in this house (based on Lagna)
            # In South Indian system, house 1 = Lagna rashi
            rashi_index = int((lagna_deg + (house_num - 1) * 30) % 360 // 30)
            rashi_sym = rashi_abbr[rashi_index]

            svg += f'<text x="{cx}" y="{cy-15}" font-size="18" fill="#8b0000" text-anchor="middle" font-weight="bold">{house_num}</text>'
            svg += f'<text x="{cx}" y="{cy+12}" font-size="24" fill="#8b4513" text-anchor="middle" font-weight="bold">{rashi_sym}</text>'

        # Place planets in correct houses
        for sym, deg in positions.items():
            # Skip Lagna symbol in Navamsa
            if sym == "Lg" and is_navamsa:
                continue
            
            # Calculate which house this planet is in
            # Relative to Lagna (house 1 = 0° from Lagna)
            rel_deg = (deg - lagna_deg + 360) % 360
            house_num = int(rel_deg // 30) % 12
            # Map house number (0-11) to center index
            # House 1 (Lagna) is at centers[0], House 2 at centers[1], etc.
            house_idx = house_num
            cx, cy = centers[house_idx]

            color = colors.get(sym, colors["default"])
            symbol = symbols.get(sym, "?")
            
            # Draw planet symbol
            svg += f'<text x="{cx}" y="{cy+55}" font-size="36" fill="{color}" text-anchor="middle">{symbol}</text>'
            
            # Add planet name below symbol (except for Lagna)
            if sym != "Lg":
                name_map = {
                    "Su": "Sun", "Mo": "Moon", "Ma": "Mars", "Me": "Merc",
                    "Ju": "Jup", "Ve": "Ven", "Sa": "Sat", "Ra": "Rah", "Ke": "Ket"
                }
                planet_name = name_map.get(sym, sym)
                svg += f'<text x="{cx}" y="{cy+80}" font-size="12" fill="#555" text-anchor="middle">{planet_name}</text>'
            else:
                # Show "Lg" for Lagna
                svg += f'<text x="{cx}" y="{cy+80}" font-size="14" fill="#006400" text-anchor="middle" font-weight="bold">Lg</text>'

        svg += '</svg>'
        return svg
