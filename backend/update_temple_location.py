"""
Script to Update Temple Location for Accurate Panchang Calculations

This script updates the temple's latitude, longitude, and city in panchang_display_settings
to ensure accurate Panchang calculations.
"""

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.panchang_display_settings import PanchangDisplaySettings
from app.models.temple import Temple  # Needed for SQLAlchemy relationship resolution

# Common Indian City Coordinates
CITY_COORDINATES = {
    "Bangalore": {"lat": "12.9716", "lon": "77.5946", "city": "Bengaluru"},
    "Bengaluru": {"lat": "12.9716", "lon": "77.5946", "city": "Bengaluru"},
    "Delhi": {"lat": "28.6139", "lon": "77.2090", "city": "Delhi"},
    "Mumbai": {"lat": "19.0760", "lon": "72.8777", "city": "Mumbai"},
    "Hyderabad": {"lat": "17.3850", "lon": "78.4867", "city": "Hyderabad"},
    "Chennai": {"lat": "13.0827", "lon": "80.2707", "city": "Chennai"},
    "Kolkata": {"lat": "22.5726", "lon": "88.3639", "city": "Kolkata"},
    "Pune": {"lat": "18.5204", "lon": "73.8567", "city": "Pune"},
    "Ahmedabad": {"lat": "23.0225", "lon": "72.5714", "city": "Ahmedabad"},
    "Jaipur": {"lat": "26.9124", "lon": "75.7873", "city": "Jaipur"},
    "Surat": {"lat": "21.1702", "lon": "72.8311", "city": "Surat"},
    "Lucknow": {"lat": "26.8467", "lon": "80.9462", "city": "Lucknow"},
    "Kanpur": {"lat": "26.4499", "lon": "80.3319", "city": "Kanpur"},
    "Nagpur": {"lat": "21.1458", "lon": "79.0882", "city": "Nagpur"},
    "Indore": {"lat": "22.7196", "lon": "75.8577", "city": "Indore"},
    "Thane": {"lat": "19.2183", "lon": "72.9781", "city": "Thane"},
    "Bhopal": {"lat": "23.2599", "lon": "77.4126", "city": "Bhopal"},
    "Visakhapatnam": {"lat": "17.6868", "lon": "83.2185", "city": "Visakhapatnam"},
    "Pimpri-Chinchwad": {"lat": "18.6298", "lon": "73.7997", "city": "Pimpri-Chinchwad"},
    "Patna": {"lat": "25.5941", "lon": "85.1376", "city": "Patna"},
    "Vadodara": {"lat": "22.3072", "lon": "73.1812", "city": "Vadodara"},
    "Ghaziabad": {"lat": "28.6692", "lon": "77.4538", "city": "Ghaziabad"},
    "Ludhiana": {"lat": "30.9010", "lon": "75.8573", "city": "Ludhiana"},
    "Agra": {"lat": "27.1767", "lon": "78.0081", "city": "Agra"},
    "Nashik": {"lat": "19.9975", "lon": "73.7898", "city": "Nashik"},
    "Faridabad": {"lat": "28.4089", "lon": "77.3178", "city": "Faridabad"},
    "Meerut": {"lat": "28.9845", "lon": "77.7064", "city": "Meerut"},
    "Rajkot": {"lat": "22.3039", "lon": "70.8022", "city": "Rajkot"},
    "Kalyan-Dombivali": {"lat": "19.2403", "lon": "73.1305", "city": "Kalyan-Dombivali"},
    "Vasai-Virar": {"lat": "19.4612", "lon": "72.7985", "city": "Vasai-Virar"},
    "Varanasi": {"lat": "25.3176", "lon": "82.9739", "city": "Varanasi"},
    "Srinagar": {"lat": "34.0837", "lon": "74.7973", "city": "Srinagar"},
    "Aurangabad": {"lat": "19.8762", "lon": "75.3433", "city": "Aurangabad"},
    "Dhanbad": {"lat": "23.7957", "lon": "86.4304", "city": "Dhanbad"},
    "Amritsar": {"lat": "31.6340", "lon": "74.8723", "city": "Amritsar"},
    "Navi Mumbai": {"lat": "19.0330", "lon": "73.0297", "city": "Navi Mumbai"},
    "Allahabad": {"lat": "25.4358", "lon": "81.8463", "city": "Allahabad"},
    "Prayagraj": {"lat": "25.4358", "lon": "81.8463", "city": "Prayagraj"},
    "Ranchi": {"lat": "23.3441", "lon": "85.3096", "city": "Ranchi"},
    "Howrah": {"lat": "22.5958", "lon": "88.2636", "city": "Howrah"},
    "Coimbatore": {"lat": "11.0168", "lon": "76.9558", "city": "Coimbatore"},
    "Jabalpur": {"lat": "23.1815", "lon": "79.9864", "city": "Jabalpur"},
    "Gwalior": {"lat": "26.2183", "lon": "78.1828", "city": "Gwalior"},
    "Vijayawada": {"lat": "16.5062", "lon": "80.6480", "city": "Vijayawada"},
    "Jodhpur": {"lat": "26.2389", "lon": "73.0243", "city": "Jodhpur"},
    "Madurai": {"lat": "9.9252", "lon": "78.1198", "city": "Madurai"},
    "Raipur": {"lat": "21.2514", "lon": "81.6296", "city": "Raipur"},
    "Kota": {"lat": "25.2138", "lon": "75.8648", "city": "Kota"},
    "Chandigarh": {"lat": "30.7333", "lon": "76.7794", "city": "Chandigarh"},
    "Guwahati": {"lat": "26.1445", "lon": "91.7362", "city": "Guwahati"},
    "Solapur": {"lat": "17.6599", "lon": "75.9064", "city": "Solapur"},
    "Hubli-Dharwad": {"lat": "15.3647", "lon": "75.1240", "city": "Hubli-Dharwad"},
    "Mysore": {"lat": "12.2958", "lon": "76.6394", "city": "Mysore"},
    "Mysuru": {"lat": "12.2958", "lon": "76.6394", "city": "Mysuru"},
    "Tiruchirappalli": {"lat": "10.7905", "lon": "78.7047", "city": "Tiruchirappalli"},
    "Bareilly": {"lat": "28.3670", "lon": "79.4304", "city": "Bareilly"},
    "Aligarh": {"lat": "27.8974", "lon": "78.0880", "city": "Aligarh"},
    "Tiruppur": {"lat": "11.1085", "lon": "77.3411", "city": "Tiruppur"},
    "Moradabad": {"lat": "28.8389", "lon": "78.7378", "city": "Moradabad"},
    "Jalandhar": {"lat": "31.3260", "lon": "75.5762", "city": "Jalandhar"},
    "Bhubaneswar": {"lat": "20.2961", "lon": "85.8245", "city": "Bhubaneswar"},
    "Salem": {"lat": "11.6643", "lon": "78.1460", "city": "Salem"},
    "Warangal": {"lat": "17.9689", "lon": "79.5941", "city": "Warangal"},
    "Mira-Bhayandar": {"lat": "19.2952", "lon": "72.8544", "city": "Mira-Bhayandar"},
    "Thiruvananthapuram": {"lat": "8.5241", "lon": "76.9366", "city": "Thiruvananthapuram"},
    "Guntur": {"lat": "16.3067", "lon": "80.4365", "city": "Guntur"},
    "Bhiwandi": {"lat": "19.3009", "lon": "73.0630", "city": "Bhiwandi"},
    "Saharanpur": {"lat": "29.9680", "lon": "77.5460", "city": "Saharanpur"},
    "Gorakhpur": {"lat": "26.7606", "lon": "83.3732", "city": "Gorakhpur"},
    "Bikaner": {"lat": "28.0229", "lon": "73.3119", "city": "Bikaner"},
    "Amravati": {"lat": "20.9374", "lon": "77.7796", "city": "Amravati"},
    "Noida": {"lat": "28.5355", "lon": "77.3910", "city": "Noida"},
    "Jamshedpur": {"lat": "22.8046", "lon": "86.2029", "city": "Jamshedpur"},
    "Bhilai": {"lat": "21.2095", "lon": "81.4293", "city": "Bhilai"},
    "Cuttack": {"lat": "20.4625", "lon": "85.8828", "city": "Cuttack"},
    "Firozabad": {"lat": "27.1592", "lon": "78.3957", "city": "Firozabad"},
    "Kochi": {"lat": "9.9312", "lon": "76.2673", "city": "Kochi"},
    "Bhavnagar": {"lat": "21.7645", "lon": "72.1519", "city": "Bhavnagar"},
    "Dehradun": {"lat": "30.3165", "lon": "78.0322", "city": "Dehradun"},
    "Durgapur": {"lat": "23.5204", "lon": "87.3119", "city": "Durgapur"},
    "Asansol": {"lat": "23.6839", "lon": "86.9523", "city": "Asansol"},
    "Nanded": {"lat": "19.1383", "lon": "77.3210", "city": "Nanded"},
    "Kolhapur": {"lat": "16.7050", "lon": "74.2433", "city": "Kolhapur"},
    "Ajmer": {"lat": "26.4499", "lon": "74.6399", "city": "Ajmer"},
    "Akola": {"lat": "20.7333", "lon": "77.0081", "city": "Akola"},
    "Gulbarga": {"lat": "17.3297", "lon": "76.8343", "city": "Gulbarga"},
    "Jamnagar": {"lat": "22.4707", "lon": "70.0577", "city": "Jamnagar"},
    "Ujjain": {"lat": "23.1793", "lon": "75.7849", "city": "Ujjain"},
    "Loni": {"lat": "28.7500", "lon": "77.2833", "city": "Loni"},
    "Siliguri": {"lat": "26.7271", "lon": "88.3953", "city": "Siliguri"},
    "Jhansi": {"lat": "25.4484", "lon": "78.5685", "city": "Jhansi"},
    "Ulhasnagar": {"lat": "19.2183", "lon": "73.1382", "city": "Ulhasnagar"},
    "Jammu": {"lat": "32.7266", "lon": "74.8570", "city": "Jammu"},
    "Mangalore": {"lat": "12.9141", "lon": "74.8560", "city": "Mangalore"},
    "Erode": {"lat": "11.3410", "lon": "77.7172", "city": "Erode"},
    "Belgaum": {"lat": "15.8497", "lon": "74.4977", "city": "Belgaum"},
    "Ambattur": {"lat": "13.1143", "lon": "80.1548", "city": "Ambattur"},
    "Tirunelveli": {"lat": "8.7139", "lon": "77.7567", "city": "Tirunelveli"},
    "Malegaon": {"lat": "20.5579", "lon": "74.5287", "city": "Malegaon"},
    "Gaya": {"lat": "24.7955", "lon": "85.0002", "city": "Gaya"},
    "Tirupati": {"lat": "13.6288", "lon": "79.4192", "city": "Tirupati"},
    "Davanagere": {"lat": "14.4644", "lon": "75.9244", "city": "Davanagere"},
    "Kozhikode": {"lat": "11.2588", "lon": "75.7804", "city": "Kozhikode"},
}


def update_temple_location(temple_id: int, city_name: str = None, latitude: str = None, longitude: str = None):
    """
    Update temple location in panchang_display_settings

    Args:
        temple_id: Temple ID
        city_name: City name (will lookup coordinates if lat/lon not provided)
        latitude: Latitude as string (e.g., "12.9716")
        longitude: Longitude as string (e.g., "77.5946")
    """
    db = SessionLocal()

    try:
        # Get or create panchang settings
        settings = db.query(PanchangDisplaySettings).filter(
            PanchangDisplaySettings.temple_id == temple_id
        ).first()

        if not settings:
            print(f"❌ No panchang settings found for temple_id={temple_id}")
            print("   Creating new settings...")
            settings = PanchangDisplaySettings(temple_id=temple_id)
            db.add(settings)

        # If city name provided, lookup coordinates
        if city_name and not latitude:
            city_data = CITY_COORDINATES.get(city_name)
            if city_data:
                latitude = city_data["lat"]
                longitude = city_data["lon"]
                city_name = city_data["city"]
                print(f"✅ Found coordinates for {city_name}")
            else:
                print(f"❌ City '{city_name}' not found in database")
                print("\n📝 Available cities:")
                for city in sorted(CITY_COORDINATES.keys())[:20]:
                    print(f"   - {city}")
                print(f"   ... and {len(CITY_COORDINATES) - 20} more")
                return

        # Update settings
        if latitude:
            settings.latitude = latitude
        if longitude:
            settings.longitude = longitude
        if city_name:
            settings.city_name = city_name

        db.commit()
        db.refresh(settings)

        print("\n" + "=" * 60)
        print("✅ Temple location updated successfully!")
        print("=" * 60)
        print(f"\n📍 Location Details:")
        print(f"   Temple ID: {temple_id}")
        print(f"   City: {settings.city_name}")
        print(f"   Latitude: {settings.latitude}")
        print(f"   Longitude: {settings.longitude}")
        print(f"   Timezone: {settings.timezone}")
        print("\n🔄 Next steps:")
        print("   1. Restart your backend server")
        print("   2. Panchang will now use these coordinates for calculations")
        print("   3. Sunrise/sunset and all timings will be accurate for this location")

    except Exception as e:
        print(f"\n❌ Error updating location: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🕉️  Temple Location Update Tool")
    print("=" * 60)
    print()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python update_temple_location.py <temple_id> <city_name>")
        print("  python update_temple_location.py <temple_id> <latitude> <longitude> <city_name>")
        print("\nExamples:")
        print("  python update_temple_location.py 1 Delhi")
        print("  python update_temple_location.py 1 28.6139 77.2090 \"New Delhi\"")
        print("\n📝 Common cities available:")
        for city in sorted(CITY_COORDINATES.keys())[:15]:
            coords = CITY_COORDINATES[city]
            print(f"   {city:20} - Lat: {coords['lat']:8}, Lon: {coords['lon']:8}")
        print(f"   ... and {len(CITY_COORDINATES) - 15} more cities")
        sys.exit(1)

    temple_id = int(sys.argv[1])

    if len(sys.argv) == 3:
        # City name provided
        city_name = sys.argv[2]
        update_temple_location(temple_id, city_name=city_name)
    elif len(sys.argv) == 5:
        # Lat, lon, city provided
        latitude = sys.argv[2]
        longitude = sys.argv[3]
        city_name = sys.argv[4]
        update_temple_location(temple_id, city_name=city_name, latitude=latitude, longitude=longitude)
    else:
        print("❌ Invalid arguments")
        print("Usage: python update_temple_location.py <temple_id> <city_name>")
        print("   OR: python update_temple_location.py <temple_id> <latitude> <longitude> <city_name>")
