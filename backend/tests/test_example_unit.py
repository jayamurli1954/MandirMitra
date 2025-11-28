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
        "day_of_week,expected_period",
        [
            (0, 1),  # Sunday -> 1st period (Kaal)
            (1, 6),  # Monday -> 6th period
            (2, 3),  # Tuesday -> 3rd period
            (3, 2),  # Wednesday -> 2nd period
            (4, 4),  # Thursday -> 4th period
            (5, 5),  # Friday -> 5th period
            (6, 7),  # Saturday -> 7th period
        ],
    )
    def test_gulika_period_calculation(self, day_of_week, expected_period):
        """Test Gulika period calculation for different days"""
        result = self.service._get_gulika_period(day_of_week)
        assert result == expected_period

    def test_tithi_names(self):
        """Test that all 30 tithi names are defined"""
        tithi_names = self.service._get_tithi_name(0)
        assert tithi_names is not None

    @pytest.mark.parametrize(
        "tithi_number,expected_name",
        [
            (0, "Pratipada"),
            (14, "Purnima"),
            (29, "Amavasya"),
        ],
    )
    def test_specific_tithi_names(self, tithi_number, expected_name):
        """Test specific tithi name mappings"""
        name = self.service._get_tithi_name(tithi_number)
        assert expected_name in name


@pytest.mark.unit
class TestStringOperations:
    """Example of simple unit tests"""

    def test_string_concatenation(self):
        """Test basic string operations"""
        result = "Hello" + " " + "World"
        assert result == "Hello World"

    def test_string_upper(self):
        """Test string uppercase conversion"""
        assert "mandirsync".upper() == "MANDIRSYNC"

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
