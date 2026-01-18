"""
Ready Reckoner Service
Pre-calculates and caches important sacred dates for quick lookup
Uses existing PanchangService for accurate calculations
"""

from datetime import date, datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.sacred_events_cache import SacredEventsCache
from app.services.panchang_service import PanchangService


class ReadyReckonerService:
    """Service to pre-calculate and provide quick lookups for sacred events"""
    
    def __init__(self, db: Session):
        self.db = db
        self.panchang_service = PanchangService()
    
    def pre_calculate_dates(
        self,
        temple_id: Optional[int],
        start_date: date,
        end_date: date,
        lat: float = 12.9716,
        lon: float = 77.5946,
        city: str = "Bengaluru"
    ) -> Dict:
        """
        Pre-calculate sacred events dates for a date range
        
        This should be called daily via background job to maintain cache
        
        Args:
            temple_id: Temple ID (None for standalone mode)
            start_date: Start date for calculations
            end_date: End date for calculations
            lat: Latitude for panchang calculations
            lon: Longitude for panchang calculations
            city: City name
            
        Returns:
            Dict with summary of calculations
        """
        print(f"Pre-calculating sacred events from {start_date} to {end_date}")
        
        current_date = start_date
        events_created = 0
        events_updated = 0
        
        # Delete existing entries for this date range to avoid duplicates
        self.db.query(SacredEventsCache).filter(
            and_(
                SacredEventsCache.temple_id == temple_id,
                SacredEventsCache.event_date >= start_date,
                SacredEventsCache.event_date <= end_date
            )
        ).delete()
        
        while current_date <= end_date:
            try:
                # Create datetime at sunrise (morning) for this date
                # Using 6:00 AM IST as approximate main seva time
                dt = datetime.combine(current_date, datetime.min.time().replace(hour=6, minute=0))
                
                # Calculate panchang using existing service (READ-ONLY - no modifications to PanchangService)
                # This is safe: we only READ from PanchangService, never modify it
                panchang = self.panchang_service.calculate_panchang(dt, lat, lon, city)
                
                # Extract tithi and nakshatra - check nested structure
                # PanchangService returns: panchang.tithi and panchang.nakshatra
                panchang_data = panchang.get('panchang', {})
                tithi_data = panchang_data.get('tithi', panchang.get('tithi', {}))
                nakshatra_data = panchang_data.get('nakshatra', panchang.get('nakshatra', {}))
                
                # Get lunar month for special Ekadashi detection
                # Use Purnimanta (North Indian) system for named Ekadashis as that's the traditional reference
                hindu_date = panchang.get('date', {}).get('hindu', {})
                lunar_month = hindu_date.get('lunar_month_purnimanta', '') or hindu_date.get('lunar_month_amanta', '')
                
                # Get weekday name
                weekday = current_date.strftime('%A')
                
                # 1. Save Nakshatra (NAK)
                if nakshatra_data and nakshatra_data.get('name'):
                    nakshatra_name = nakshatra_data['name']
                    self._save_event(
                        temple_id=temple_id,
                        event_code='NAK',
                        event_name=nakshatra_name,
                        event_date=current_date,
                        weekday=weekday,
                        extra_info=f"Star number: {nakshatra_data.get('number', '')}"
                    )
                    events_created += 1
                
                # 2. Check for Ekadashi (EK) - tithi number 11
                # Also check for special date-based Ekadashis (like Vaikunta Ekadashi on Dec 30, 2025)
                is_ekadashi_tithi = tithi_data.get('number') == 11
                is_special_ekadashi_date = False
                
                # Special date check for Vaikunta Ekadashi (Dec 30, 2025) even if tithi is 10 or 12
                if current_date == date(2025, 12, 30) and tithi_data.get('paksha') == 'Shukla':
                    # Check if we're close to Ekadashi (Dashami or Dwadashi in Margashirsha/Agrahayana)
                    if tithi_data.get('number') in [10, 11, 12]:
                        hindu_date = panchang.get('date', {}).get('hindu', {})
                        lunar_month = hindu_date.get('lunar_month_purnimanta', '') or hindu_date.get('lunar_month_amanta', '')
                        month_lower = lunar_month.lower() if lunar_month else ''
                        if 'margashirsha' in month_lower or 'agrahayana' in month_lower:
                            is_special_ekadashi_date = True
                
                if is_ekadashi_tithi or is_special_ekadashi_date:
                    paksha = tithi_data.get('paksha', '')
                    
                    # Check for special named Ekadashis
                    event_name = self._get_ekadashi_name(paksha, lunar_month, current_date)
                    extra_info = paksha
                    
                    # Add lunar month info for special Ekadashis
                    if event_name != f"{paksha} Ekadashi" if paksha else "Ekadashi":
                        extra_info = f"{lunar_month} {paksha}"
                    
                    self._save_event(
                        temple_id=temple_id,
                        event_code='EK',
                        event_name=event_name,
                        event_date=current_date,
                        weekday=weekday,
                        extra_info=extra_info
                    )
                    events_created += 1
                
                # 3. Check for Sankashta Chaturthi (SK) - Krishna Paksha Chaturthi (tithi 4)
                if tithi_data.get('number') == 4 and tithi_data.get('paksha') == 'Krishna':
                    self._save_event(
                        temple_id=temple_id,
                        event_code='SK',
                        event_name='Sankashta Chaturthi',
                        event_date=current_date,
                        weekday=weekday
                    )
                    events_created += 1
                
                # 4. Check for Pradosha (PR) - Trayodashi (tithi 13)
                if tithi_data.get('number') == 13:
                    paksha = tithi_data.get('paksha', '')
                    event_name = f"{paksha} Pradosha" if paksha else "Pradosha"
                    self._save_event(
                        temple_id=temple_id,
                        event_code='PR',
                        event_name=event_name,
                        event_date=current_date,
                        weekday=weekday,
                        extra_info=paksha
                    )
                    events_created += 1
                
                # 5. Check for Pournami (PM) - Full Moon (Shukla Paksha Tithi 15, or Purnima)
                if (tithi_data.get('name') == 'Purnima' or 
                    (tithi_data.get('number') == 15 and tithi_data.get('paksha') == 'Shukla')):
                    self._save_event(
                        temple_id=temple_id,
                        event_code='PM',
                        event_name='Pournami',
                        event_date=current_date,
                        weekday=weekday
                    )
                    events_created += 1
                
                # 6. Check for Amavasya (AM) - New Moon
                if tithi_data.get('name') == 'Amavasya':
                    self._save_event(
                        temple_id=temple_id,
                        event_code='AM',
                        event_name='Amavasya',
                        event_date=current_date,
                        weekday=weekday
                    )
                    events_created += 1
                
            except Exception as e:
                print(f"Error calculating events for {current_date}: {e}")
                continue
            
            current_date += timedelta(days=1)
        
        # Commit all changes
        self.db.commit()
        
        print(f"Pre-calculation complete. Created {events_created} events")
        
        return {
            "status": "success",
            "events_created": events_created,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    
    def _get_ekadashi_name(self, paksha: str, lunar_month: str, event_date: date) -> str:
        """
        Get the proper name for Ekadashi, including special named Ekadashis
        
        Args:
            paksha: Shukla or Krishna
            lunar_month: Lunar month name (e.g., 'Margashirsha', 'Agrahayana')
            event_date: Date of the Ekadashi
            
        Returns:
            Proper name for the Ekadashi
        """
        # Normalize lunar month name (handle variations)
        # Note: Amanta system uses "Agrahayana" while Purnimanta uses "Margashirsha" for the same period
        month_lower = lunar_month.lower() if lunar_month else ''
        
        # IMPORTANT FESTIVAL OVERRIDES - Date-based checks for well-known festivals
        # Vaikunta Ekadashi - Dec 30, 2025 (very important, user-confirmed date)
        if event_date == date(2025, 12, 30) and paksha == 'Shukla':
            return 'Vaikunta Ekadashi (Mokshada Ekadashi)'
        
        # Vaikunta Ekadashi - Shukla Paksha Ekadashi in Margashirsha month (Dhanurmasa)
        # Also known as Mokshada Ekadashi
        # Check both Margashirsha (Purnimanta) and Agrahayana (Amanta - South Indian)
        if paksha == 'Shukla' and ('margashirsha' in month_lower or 'agrahayana' in month_lower):
            return 'Vaikunta Ekadashi (Mokshada Ekadashi)'
        
        # Putrada Ekadashi - Shukla Paksha Ekadashi in Pausha month
        if paksha == 'Shukla' and 'pausha' in month_lower:
            return 'Putrada Ekadashi'
        
        # Satila Ekadashi / Jaya Ekadashi - Shukla Paksha Ekadashi in Magha month
        if paksha == 'Shukla' and 'magha' in month_lower:
            return 'Jaya Ekadashi'
        
        # Amalaki Ekadashi - Shukla Paksha Ekadashi in Phalguna month
        if paksha == 'Shukla' and 'phalguna' in month_lower:
            return 'Amalaki Ekadashi'
        
        # Papamochani Ekadashi - Krishna Paksha Ekadashi in Chaitra month
        if paksha == 'Krishna' and 'chaitra' in month_lower:
            return 'Papamochani Ekadashi'
        
        # Varuthini Ekadashi - Krishna Paksha Ekadashi in Vaishakha month
        if paksha == 'Krishna' and 'vaishakha' in month_lower:
            return 'Varuthini Ekadashi'
        
        # Nirjala Ekadashi - Jyeshtha Shukla Paksha Ekadashi (very important)
        if paksha == 'Shukla' and 'jyeshtha' in month_lower:
            return 'Nirjala Ekadashi'
        
        # Devshayani Ekadashi - Ashadha Shukla Paksha Ekadashi (start of Chaturmasa)
        if paksha == 'Shukla' and 'ashadha' in month_lower:
            return 'Devshayani Ekadashi (Ashadi Ekadashi)'
        
        # Kamika Ekadashi - Shravana Krishna Paksha Ekadashi
        if paksha == 'Krishna' and 'shravana' in month_lower:
            return 'Kamika Ekadashi'
        
        # Parsva Ekadashi / Vamana Ekadashi - Bhadrapada Shukla Paksha Ekadashi
        if paksha == 'Shukla' and 'bhadrapada' in month_lower:
            return 'Vamana Ekadashi (Parsva Ekadashi)'
        
        # Indira Ekadashi - Ashwin Krishna Paksha Ekadashi
        if paksha == 'Krishna' and 'ashwin' in month_lower:
            return 'Indira Ekadashi'
        
        # Prabodhini Ekadashi / Devutthana Ekadashi - Kartika Shukla Paksha Ekadashi (end of Chaturmasa)
        if paksha == 'Shukla' and 'kartika' in month_lower:
            return 'Prabodhini Ekadashi (Devutthana Ekadashi)'
        
        # Utpanna Ekadashi - Kartika Krishna Paksha Ekadashi
        if paksha == 'Krishna' and 'kartika' in month_lower:
            return 'Utpanna Ekadashi'
        
        # Default: return generic Ekadashi name
        return f"{paksha} Ekadashi" if paksha else "Ekadashi"
    
    def _save_event(
        self,
        temple_id: Optional[int],
        event_code: str,
        event_name: str,
        event_date: date,
        weekday: str,
        extra_info: Optional[str] = None
    ):
        """Save or update a sacred event in cache"""
        # Check if event already exists for this date
        existing = self.db.query(SacredEventsCache).filter(
            and_(
                SacredEventsCache.temple_id == temple_id,
                SacredEventsCache.event_code == event_code,
                SacredEventsCache.event_date == event_date
            )
        ).first()
        
        if existing:
            # Update existing
            existing.event_name = event_name
            existing.weekday = weekday
            existing.extra_info = extra_info
        else:
            # Create new
            event = SacredEventsCache(
                temple_id=temple_id,
                event_code=event_code,
                event_name=event_name,
                event_date=event_date,
                weekday=weekday,
                extra_info=extra_info,
                valid_from=event_date,
                valid_to=event_date + timedelta(days=365)  # Valid for 1 year
            )
            self.db.add(event)
    
    def get_upcoming_events(
        self,
        temple_id: Optional[int],
        event_code: Optional[str] = None,
        limit: int = 10,
        start_date: Optional[date] = None
    ) -> List[Dict]:
        """
        Get upcoming sacred events from cache
        
        Args:
            temple_id: Temple ID (None for standalone)
            event_code: Filter by event code ('NAK', 'EK', 'SK', 'PR', 'PM', 'AM') or None for all
            limit: Maximum number of events to return
            start_date: Start searching from this date (default: today)
            
        Returns:
            List of event dictionaries
        """
        if start_date is None:
            start_date = date.today()
        
        # Build query
        query = self.db.query(SacredEventsCache).filter(
            and_(
                SacredEventsCache.temple_id == temple_id,
                SacredEventsCache.event_date >= start_date
            )
        )
        
        # Filter by event code if specified
        if event_code:
            query = query.filter(SacredEventsCache.event_code == event_code)
        
        # Order by date and limit
        events = query.order_by(SacredEventsCache.event_date).limit(limit).all()
        
        # Convert to dictionaries
        result = []
        for event in events:
            days_away = (event.event_date - start_date).days
            result.append({
                "event_code": event.event_code,
                "event_name": event.event_name,
                "event_date": event.event_date.isoformat(),
                "weekday": event.weekday,
                "days_away": days_away,
                "is_today": days_away == 0,
                "extra_info": event.extra_info
            })
        
        return result
    
    def get_dashboard_data(
        self,
        temple_id: Optional[int],
        start_date: Optional[date] = None
    ) -> Dict:
        """
        Get complete dashboard data with all upcoming sacred events
        
        Args:
            temple_id: Temple ID
            start_date: Start date (default: today)
            
        Returns:
            Dict with today's nakshatra and upcoming events by type
        """
        if start_date is None:
            start_date = date.today()
        
        # Get today's nakshatra
        today_nakshatra = None
        today_events = self.get_upcoming_events(temple_id, event_code='NAK', limit=1, start_date=start_date)
        if today_events and today_events[0]['is_today']:
            today_nakshatra = today_events[0]['event_name']
        elif today_events:
            # If today's nakshatra not in cache, get from panchang directly
            try:
                dt = datetime.combine(start_date, datetime.min.time().replace(hour=6, minute=0))
                panchang = self.panchang_service.calculate_panchang(dt, 12.9716, 77.5946, "Bengaluru")
                today_nakshatra = panchang.get('nakshatra', {}).get('name', 'Unknown')
            except:
                today_nakshatra = 'Unknown'
        
        # Get upcoming events by type
        result = {
            "today": start_date.isoformat(),
            "today_nakshatra": today_nakshatra,
            "events": {
                "ekadashi": self.get_upcoming_events(temple_id, 'EK', limit=5, start_date=start_date),
                "pradosha": self.get_upcoming_events(temple_id, 'PR', limit=5, start_date=start_date),
                "sankashta": self.get_upcoming_events(temple_id, 'SK', limit=5, start_date=start_date),
                "pournami": self.get_upcoming_events(temple_id, 'PM', limit=5, start_date=start_date),
                "amavasya": self.get_upcoming_events(temple_id, 'AM', limit=5, start_date=start_date),
                "nakshatra": self.get_upcoming_events(temple_id, 'NAK', limit=5, start_date=start_date)
            }
        }
        
        return result
    
    def find_next_nakshatra(
        self,
        temple_id: Optional[int],
        nakshatra_name: str,
        limit: int = 5,
        start_date: Optional[date] = None
    ) -> Dict:
        """
        Find next occurrences of a specific nakshatra
        
        Args:
            temple_id: Temple ID
            nakshatra_name: Name of nakshatra (e.g., "Rohini")
            limit: Number of occurrences to return
            start_date: Start searching from this date
            
        Returns:
            Dict with nakshatra info and next occurrences
        """
        if start_date is None:
            start_date = date.today()
        
        # Get today's nakshatra
        today_nakshatra = None
        try:
            dt = datetime.combine(start_date, datetime.min.time().replace(hour=6, minute=0))
            panchang = self.panchang_service.calculate_panchang(dt, 12.9716, 77.5946, "Bengaluru")
            today_nakshatra = panchang.get('nakshatra', {}).get('name', 'Unknown')
        except:
            today_nakshatra = 'Unknown'
        
        # Query cache for this nakshatra
        events = self.db.query(SacredEventsCache).filter(
            and_(
                SacredEventsCache.temple_id == temple_id,
                SacredEventsCache.event_code == 'NAK',
                SacredEventsCache.event_name == nakshatra_name,
                SacredEventsCache.event_date >= start_date
            )
        ).order_by(SacredEventsCache.event_date).limit(limit).all()
        
        next_occurrences = []
        for event in events:
            days_away = (event.event_date - start_date).days
            next_occurrences.append({
                "event_name": event.event_name,
                "event_date": event.event_date.isoformat(),
                "weekday": event.weekday,
                "days_away": days_away,
                "is_today": days_away == 0
            })
        
        return {
            "nakshatra_name": nakshatra_name,
            "today_nakshatra": today_nakshatra,
            "is_today": today_nakshatra == nakshatra_name,
            "next_occurrences": next_occurrences
        }

