from app.services.panchang import PanchangService
from datetime import datetime

svc = PanchangService()
dt = datetime(2026, 2, 25, 10, 0, 0)
jd = svc.get_julian_day(dt)

print(f"Tithi: {svc.get_tithi(jd)['name']}")
print(f"Nakshatra: {svc.get_nakshatra(jd)['name']}")
print(f"Yoga: {svc.get_yoga(jd)['name']}")
print(f"Karana: {svc.get_karana(jd)['current']}")
