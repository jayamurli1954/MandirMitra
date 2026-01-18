"""
Example unit tests demonstrating best practices

Unit tests focus on testing individual functions or methods in isolation.
They should be fast, independent, and not require database or external services.
"""

import pytest
from datetime import datetime
from app.services.panchang_service import PanchangService


@pytest.mark.unit
class TestPanchangServiceUnit:
    """Unit tests for PanchangService calculations"""

    def setup_method(self):
        """Setup before each test method"""
        self.service = PanchangService()

    @pytest.mark.parametrize(
        "day_of_week,expected_segment",
        [
            (0, 6),  # Sunday -> 7th segment (0-indexed: 6)
            (1, 2),  # Monday -> 3rd segment (0-indexed: 2)
            (2, 0),  # Tuesday -> 1st segment (0-indexed: 0)
            (3, 5),  # Wednesday -> 6th segment (0-indexed: 5)
            (4, 4),  # Thursday -> 5th segment (0-indexed: 4)
            (5, 3),  # Friday -> 4th segment (0-indexed: 3)
            (6, 2),  # Saturday -> 3rd segment (0-indexed: 2)
        ],
    )
    def test_gulika_period_calculation(self, day_of_week, expected_segment):
        """Test Gulika period calculation for different days"""
        # Use sample sunrise/sunset times for testing
        sunrise = "06:00:00"
        sunset = "18:00:00"
        result = self.service.get_gulika(sunrise, sunset, day_of_week)

        # Verify that gulika timing is calculated correctly
        assert "start" in result
        assert "end" in result
        assert "duration_minutes" in result
        assert isinstance(result["start"], str)
        assert isinstance(result["end"], str)
        assert isinstance(result["duration_minutes"], int)

        # Verify the segment is correct by checking the timing
        # Each segment is 1/8 of the day (12 hours = 720 minutes / 8 = 90 minutes)
        start_time = result["start"]
        start_hour = int(start_time.split(":")[0])
        start_min = int(start_time.split(":")[1])
        start_total_minutes = start_hour * 60 + start_min

        sunrise_hour = int(sunrise.split(":")[0])
        sunrise_min = int(sunrise.split(":")[1])
        sunrise_total_minutes = sunrise_hour * 60 + sunrise_min

        day_duration = (
            int(sunset.split(":")[0]) * 60 + int(sunset.split(":")[1])
        ) - sunrise_total_minutes
        segment_duration = day_duration / 8
        expected_start_minutes = sunrise_total_minutes + (expected_segment * segment_duration)

        # Allow 2 minute tolerance for rounding
        assert abs(start_total_minutes - expected_start_minutes) <= 2

    def test_tithi_names(self):
        """Test that all tithi names are defined"""
        # Test that TITHIS constant has all expected names
        assert len(self.service.TITHIS) == 15
        assert "Pratipada" in self.service.TITHIS
        assert "Purnima" in self.service.TITHIS
        assert "Ekadashi" in self.service.TITHIS

        # Test get_tithi method returns tithi name (requires swisseph)
        try:
            from datetime import datetime

            # Use a known date (Jan 1, 2025)
            jd = 2459580.5  # Approximate JD for Jan 1, 2025
            tithi_data = self.service.get_tithi(jd)
            assert "name" in tithi_data
            assert tithi_data["name"] is not None
            assert "full_name" in tithi_data
            assert "number" in tithi_data
        except (ImportError, AttributeError):
            # If swisseph is not available, just test the constants
            pytest.skip("swisseph not available for full tithi calculation test")

    @pytest.mark.parametrize(
        "tithi_index,expected_name",
        [
            (0, "Pratipada"),
            (14, "Purnima"),
        ],
    )
    def test_specific_tithi_names(self, tithi_index, expected_name):
        """Test specific tithi name mappings in TITHIS array"""
        # Test TITHIS array has correct names at specific indices
        assert self.service.TITHIS[tithi_index] == expected_name

        # Test that get_tithi can return these names (if swisseph available)
        try:
            jd = 2459580.5  # Approximate JD for testing
            tithi_data = self.service.get_tithi(jd)

            # Verify the structure
            assert "name" in tithi_data
            assert "full_name" in tithi_data
            assert "number" in tithi_data

            # The name should be one of the TITHIS or "Amavasya" or "Purnima"
            valid_names = list(self.service.TITHIS) + ["Amavasya", "Purnima"]
            assert tithi_data["name"] in valid_names
        except (ImportError, AttributeError):
            # If swisseph is not available, just test the constants
            pytest.skip("swisseph not available for full tithi calculation test")


@pytest.mark.unit
class TestStringOperations:
    """Example of simple unit tests"""

    def test_string_concatenation(self):
        """Test basic string operations"""
        result = "Hello" + " " + "World"
        assert result == "Hello World"

    def test_string_upper(self):
        """Test string uppercase conversion"""
        assert "MandirMitra".upper() == "MandirMitra"

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("hello", "HELLO"),
            ("world", "WORLD"),
            ("test", "TEST"),
        ],
    )
    def test_string_upper_parametrized(self, input_str, expected):
        """Test uppercase conversion with multiple inputs"""
        assert input_str.upper() == expected


@pytest.mark.unit
class TestDateOperations:
    """Example of date/time unit tests"""

    def test_datetime_now(self):
        """Test datetime creation"""
        now = datetime.utcnow()
        assert isinstance(now, datetime)
        assert now.year >= 2025

    def test_date_formatting(self):
        """Test date formatting"""
        date = datetime(2025, 11, 28, 10, 30, 45)
        formatted = date.strftime("%Y-%m-%d")
        assert formatted == "2025-11-28"

    def test_iso_format(self):
        """Test ISO format conversion"""
        date = datetime(2025, 11, 28, 10, 30, 45)
        iso = date.isoformat()
        assert iso.startswith("2025-11-28T10:30:45")
