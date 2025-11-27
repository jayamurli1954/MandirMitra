"""
Test script to verify Panchang bug fixes
"""
from app.services.panchang_service import PanchangService
from datetime import datetime

def test_panchang_fixes():
    """Test all critical Panchang fixes"""
    ps = PanchangService()
    
    # Test date: Monday, November 24, 2025 (Bangalore)
    test_date = datetime(2025, 11, 24)
    result = ps.calculate_panchang(test_date, 12.9716, 77.5946, 'Bangalore')
    
    print("=" * 70)
    print("PANCHANG BUG FIXES VERIFICATION")
    print("=" * 70)
    print(f"\nTest Date: {test_date.strftime('%A, %B %d, %Y')}")
    print(f"Location: Bangalore (12.9716°N, 77.5946°E)\n")
    
    # Test 1: Gulika Calculation (Monday should be at 6th period)
    print("1. GULIKA CALCULATION (Monday):")
    gulika = result["inauspicious_times"]["gulika"]
    print(f"   Start: {gulika['start']}")
    print(f"   End: {gulika['end']}")
    print(f"   Expected: 6th period (around 1:32-2:58 PM)")
    print(f"   Status: {'✅ PASS' if '13:' in gulika['start'] or '14:' in gulika['start'] else '❌ FAIL'}")
    
    # Test 2: Karana Display
    print("\n2. KARANA DISPLAY:")
    karana = result["panchang"]["karana"]
    print(f"   Current: {karana.get('current', 'MISSING')}")
    print(f"   End Time: {karana.get('end_time_formatted', 'MISSING')}")
    print(f"   Is Bhadra: {karana.get('is_bhadra', False)}")
    print(f"   Status: {'✅ PASS' if karana.get('current') and karana.get('end_time_formatted') else '❌ FAIL'}")
    
    # Test 3: Tithi End Time
    print("\n3. TITHI END TIME:")
    tithi = result["panchang"]["tithi"]
    print(f"   Name: {tithi.get('full_name', 'MISSING')}")
    print(f"   End Time: {tithi.get('end_time_formatted', 'MISSING')}")
    print(f"   Next Tithi: {tithi.get('next_tithi', 'MISSING')}")
    print(f"   Status: {'✅ PASS' if tithi.get('end_time_formatted') else '❌ FAIL'}")
    
    # Test 4: Nakshatra End Time
    print("\n4. NAKSHATRA END TIME:")
    nakshatra = result["panchang"]["nakshatra"]
    print(f"   Name: {nakshatra.get('name', 'MISSING')}")
    print(f"   End Time: {nakshatra.get('end_time_formatted', 'MISSING')}")
    print(f"   Next Nakshatra: {nakshatra.get('next_nakshatra', 'MISSING')}")
    print(f"   Status: {'✅ PASS' if nakshatra.get('end_time_formatted') else '❌ FAIL'}")
    
    # Test 5: Brahma Muhurat
    print("\n5. BRAHMA MUHURAT:")
    brahma = result["auspicious_times"].get("brahma_muhurat", {})
    print(f"   Start: {brahma.get('start', 'MISSING')}")
    print(f"   End: {brahma.get('end', 'MISSING')}")
    print(f"   Duration: {brahma.get('duration_minutes', 'MISSING')} minutes")
    print(f"   Status: {'✅ PASS' if brahma.get('start') else '❌ FAIL'}")
    
    # Test 6: Moonrise/Moonset
    print("\n6. MOONRISE/MOONSET:")
    moonrise = result["sun_moon"].get("moonrise")
    moonset = result["sun_moon"].get("moonset")
    print(f"   Moonrise: {moonrise if moonrise else 'Not available (normal for some dates)'}")
    print(f"   Moonset: {moonset if moonset else 'Not available (normal for some dates)'}")
    print(f"   Status: {'✅ PASS' if moonrise or moonset else '⚠️  INFO (may be None for some dates)'}")
    
    # Test 7: Hindu Calendar
    print("\n7. HINDU CALENDAR:")
    hindu = result["date"]["hindu"]
    print(f"   Vikram Samvat: {hindu.get('vikram_samvat', 'MISSING')}")
    print(f"   Shaka Samvat: {hindu.get('shaka_samvat', 'MISSING')}")
    print(f"   Lunar Month: {hindu.get('lunar_month_purnimanta', 'MISSING')}")
    print(f"   Status: {'✅ PASS' if hindu.get('vikram_samvat') else '❌ FAIL'}")
    
    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    print("\nCompare with Drik Panchang: https://www.drikpanchang.com")
    print("Select: Bangalore, November 24, 2025\n")

if __name__ == "__main__":
    test_panchang_fixes()






