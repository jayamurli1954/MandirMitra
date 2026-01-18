
import pytest
from datetime import datetime, timedelta
from app.services.panchang_service import PanchangService

@pytest.fixture
def service():
    return PanchangService()

def test_gulika_timings(service):
    """Test Gulika timings for all days of the week"""
    # Use a fixed date regarding sunrise/sunset to have predictable segments
    # We'll stick to Monday Nov 24, 2025 for now to verify the fix
    # Sunrise ~06:25, Sunset ~17:46 in Bangalore (Winter)
    # Day duration ~11h 21m = 681 mins. Segment ~85 mins.
    # Monday Gulika is 6th segment (Index 5).
    # Start = Sunrise + 5 * 85 = 06:25 + 425m = 06:25 + 7h 05m = 13:30.
    
    dt = datetime(2025, 11, 24) # Monday
    # We can mock get_sun_rise_set or just rely on internal calculation if we trust it
    # But calculate_panchang calls it.
    
    panchang = service.calculate_panchang(dt, 12.9716, 77.5946, "Bangalore")
    gulika = panchang["inauspicious_times"]["gulika"]
    
    print(f"Gulika Start: {gulika['start']}")
    
    # Check if start time is around 13:30 (1:30 PM)
    # Allow some margin for actual sunrise time variations
    assert "13:" in gulika['start'] or "14:" in gulika['start']

def test_nakshatra_end_time(service):
    """Verify Nakshatra has an end time calculated"""
    dt = datetime(2025, 11, 24)
    panchang = service.calculate_panchang(dt)
    nak = panchang["panchang"]["nakshatra"]
    
    assert nak["end_time"] is not None
    assert nak["end_time_formatted"] is not None
    print(f"Nakshatra End: {nak['end_time_formatted']}")

def test_karana_end_time(service):
    """Verify Karana has an end time calculated"""
    dt = datetime(2025, 11, 24)
    panchang = service.calculate_panchang(dt)
    karana = panchang["panchang"]["karana"]
    
    assert karana.get("end_time_formatted") is not None
    print(f"Karana End: {karana['end_time_formatted']}")

def test_samvatsara_names(service):
    """Verify Samvatsara names for recent years"""
    # 2024-25 -> Krodhi (Shaka 1946)
    # 2025-26 -> Vishwavasu (Shaka 1947)
    
    s_2024 = service.get_samvatsara(2024)
    # Note: get_samvatsara takes year and assumes it's consistent for the year
    # Usually changes in March/April. The simple logic might just take int(year).
    # If logic is (year - 78 + 11) % 60:
    # 2024: (1946 + 11) % 60 = 37 => index 37 => "Krodhin"
    assert s_2024["name"] == "Krodhin"
    
    s_2025 = service.get_samvatsara(2025)
    # 2025: (1947 + 11) % 60 = 38 => index 38 => "Vishvavasu"
    assert s_2025["name"] == "Vishvavasu"

def test_vara_logic(service):
    """Test Vara logic (though we didn't change it deeply yet, just verified)"""
    # Monday Nov 24 2025
    dt = datetime(2025, 11, 24, 10, 0, 0)
    vara = service.get_vara(dt)
    assert vara["name"] == "Monday"
