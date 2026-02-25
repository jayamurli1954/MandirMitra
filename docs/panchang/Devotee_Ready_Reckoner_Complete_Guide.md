# ðŸ"… DEVOTEE READY RECKONER - COMPLETE IMPLEMENTATION GUIDE
## For MandirMitra Temple Management Software

**Purpose:** Quick reference widget for temple counter clerks  
**Target Users:** Counter staff, devotees, priests  
**Complexity Level:** Beginner-friendly with step-by-step guidance  
**Last Updated:** December 2025

---

# TABLE OF CONTENTS

1. [Overview & Problem Statement](#section-1)
2. [What We're Building](#section-2)
3. [Data Structure & Storage](#section-3)
4. [Backend Implementation (FastAPI)](#section-4)
5. [Frontend Widget (React)](#section-5)
6. [Integration with Existing Panchang](#section-6)
7. [Step-by-Step Build Guide](#section-7)
8. [Testing & Verification](#section-8)
9. [Cursor AI Prompts](#section-9)

---

<a name="section-1"></a>
# 1. OVERVIEW & PROBLEM STATEMENT

## 1.1 The Problem

**Scenario at Temple Counter:**

```
Devotee: "I want to book Satyanarayana Pooja on my birth star"
Clerk: "What is your birth star?"
Devotee: "Rohini"
Clerk: *Opens panchang, checks today - not Rohini*
Clerk: *Manually checks next day, next day, next day...*
Clerk: "Please wait 5 minutes while I find Rohini date"

âŒ PROBLEM: Too slow, error-prone, frustrating
```

**What Clerk Needs:**

```
Clerk: *Opens Ready Reckoner widget*
Clerk: *Selects "Rohini" from dropdown*
Widget: *Instantly shows*
  - Today's Star: Krittika
  - Next Rohini: December 10, 2025 (6 days)
  - Following Rohini: January 6, 2026
Clerk: "Your star Rohini is on December 10. Would you like to book?"

âœ… SOLUTION: Instant, accurate, professional
```

## 1.2 Events to Cover

| Code | Event Name | Frequency | Importance |
|------|------------|-----------|------------|
| NAK | Nakshatra (27 stars) | Daily rotation | â­â­â­â­â­ CRITICAL |
| EK | Ekadashi | Twice/month | â­â­â­â­â­ CRITICAL |
| SK | Sankashta Chaturthi | Monthly | â­â­â­â­ HIGH |
| PR | Pradosha | Twice/month | â­â­â­â­ HIGH |
| PM | Pournami (Full Moon) | Monthly | â­â­â­ MEDIUM |
| AM | Amavasya (New Moon) | Monthly | â­â­â­ MEDIUM |

## 1.3 Success Criteria

âœ… Clerk finds date in < 5 seconds  
âœ… Shows next 3-5 occurrences  
âœ… Works offline (pre-calculated)  
âœ… Mobile responsive  
âœ… Printable reference sheet  
âœ… Updates automatically daily

---

<a name="section-2"></a>
# 2. WHAT WE'RE BUILDING

## 2.1 Widget Visual Design

```
â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
â"‚  ðŸ"… DEVOTEE READY RECKONER                        â"‚
â"œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"¤
â"‚                                                  â"‚
â"‚  Quick Find:                                     â"‚
â"‚  â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"  â"‚
â"‚  â"‚ [Select Event Type âˆ]              [Find] â"‚  â"‚
â"‚  â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜  â"‚
â"‚                                                  â"‚
â"‚  Today: Thursday, December 4, 2025               â"‚
â"‚  Current Star: Krittika                          â"‚
â"‚                                                  â"‚
â"‚  â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"â"  â"‚
â"‚                                                  â"‚
â"‚  ðŸ"† UPCOMING IMPORTANT DATES                     â"‚
â"‚                                                  â"‚
â"‚  â­ Ekadashi                                     â"‚
â"‚    â€¢ Next: Dec 7 (Sat) - 3 days                  â"‚
â"‚    â€¢ Following: Dec 21 (Sat) - 17 days           â"‚
â"‚                                                  â"‚
â"‚  ðŸ™ Pradosha                                     â"‚
â"‚    â€¢ Next: Dec 8 (Sun) - 4 days                  â"‚
â"‚    â€¢ Following: Dec 23 (Mon) - 19 days           â"‚
â"‚                                                  â"‚
â"‚  ðŸŒ™ Sankashta Chaturthi                         â"‚
â"‚    â€¢ Next: Dec 18 (Wed) - 14 days                â"‚
â"‚                                                  â"‚
â"‚  ðŸŒ• Pournami (Full Moon)                        â"‚
â"‚    â€¢ Next: Dec 15 (Sun) - 11 days                â"‚
â"‚                                                  â"‚
â"‚  [View Full Calendar] [Print Reference]          â"‚
â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
```

## 2.2 Star (Nakshatra) Finder Detail

```
â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
â"‚  ðŸ"† FIND BIRTH STAR DATE                         â"‚
â"œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"¤
â"‚                                                  â"‚
â"‚  Select Birth Star:                              â"‚
â"‚  â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"  â"‚
â"‚  â"‚ Rohini (à¤°à¥‹à¤¹à¤¿à¤£à¥€) âˆ                       â"‚  â"‚
â"‚  â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜  â"‚
â"‚                                                  â"‚
â"‚  â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"  â"‚
â"‚  â"‚ RESULTS FOR ROHINI                        â"‚  â"‚
â"‚  â"œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"¤  â"‚
â"‚  â"‚                                            â"‚  â"‚
â"‚  â"‚ Today: Krittika (Not Rohini)              â"‚  â"‚
â"‚  â"‚                                            â"‚  â"‚
â"‚  â"‚ â­ NEXT OCCURRENCES:                       â"‚  â"‚
â"‚  â"‚                                            â"‚  â"‚
â"‚  â"‚ 1. Tuesday, Dec 10, 2025                  â"‚  â"‚
â"‚  â"‚    In 6 days                               â"‚  â"‚
â"‚  â"‚    [Book Seva]                             â"‚  â"‚
â"‚  â"‚                                            â"‚  â"‚
â"‚  â"‚ 2. Monday, Jan 6, 2026                    â"‚  â"‚
â"‚  â"‚    In 33 days                              â"‚  â"‚
â"‚  â"‚    [Book Seva]                             â"‚  â"‚
â"‚  â"‚                                            â"‚  â"‚
â"‚  â"‚ 3. Sunday, Feb 2, 2026                    â"‚  â"‚
â"‚  â"‚    In 60 days                              â"‚  â"‚
â"‚  â"‚    [Book Seva]                             â"‚  â"‚
â"‚  â"‚                                            â"‚  â"‚
â"‚  â"‚ [Print Calendar] [View All Dates]         â"‚  â"‚
â"‚  â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜  â"‚
â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
```

## 2.3 Features List

### Core Features:
âœ… Quick dropdown to select event type  
âœ… Instant display of next 3-5 occurrences  
âœ… Days remaining counter  
âœ… Direct booking link integration  
âœ… Multi-language support (English, Hindi, Kannada)

### Advanced Features:
âœ… Print-friendly reference sheet  
âœ… Offline mode (pre-calculated dates)  
âœ… Mobile responsive design  
âœ… SMS/WhatsApp share functionality  
âœ… Auto-refresh at midnight  
âœ… Calendar export (iCal format)

---

<a name="section-3"></a>
# 3. DATA STRUCTURE & STORAGE

## 3.1 Database Schema

### Table: `important_dates`

```sql
CREATE TABLE important_dates (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(10) NOT NULL,  -- 'NAK', 'EK', 'SK', 'PR', 'PM', 'AM'
    event_name VARCHAR(100),           -- e.g., 'Rohini', 'Ekadashi'
    event_date DATE NOT NULL,
    event_time TIME,                   -- Time when event starts
    end_time TIME,                     -- Time when event ends
    hindu_month VARCHAR(50),           -- e.g., 'Margashirsha'
    paksha VARCHAR(20),                -- 'Shukla' or 'Krishna'
    tithi_number INT,                  -- For reference
    nakshatra_number INT,              -- 1-27 for nakshatras
    location_id INT,                   -- For multi-location support
    calculated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Indexes for fast lookup
    INDEX idx_event_type (event_type),
    INDEX idx_event_date (event_date),
    INDEX idx_nakshatra_number (nakshatra_number),
    INDEX idx_combined (event_type, event_date)
);
```

### Sample Data:

```sql
-- Nakshatra entries (27 stars rotating)
INSERT INTO important_dates 
    (event_type, event_name, event_date, event_time, nakshatra_number)
VALUES 
    ('NAK', 'Ashwini', '2025-12-05', '08:30:00', 1),
    ('NAK', 'Bharani', '2025-12-06', '09:15:00', 2),
    ('NAK', 'Krittika', '2025-12-07', '10:00:00', 3),
    ('NAK', 'Rohini', '2025-12-10', '11:45:00', 4),
    -- ... continue for all 27 nakshatras

-- Ekadashi entries
INSERT INTO important_dates 
    (event_type, event_name, event_date, event_time, hindu_month, paksha)
VALUES 
    ('EK', 'Utpanna Ekadashi', '2025-12-07', '06:30:00', 'Margashirsha', 'Krishna'),
    ('EK', 'Mokshada Ekadashi', '2025-12-21', '06:35:00', 'Margashirsha', 'Shukla'),
    -- ... continue

-- Pradosha entries
INSERT INTO important_dates 
    (event_type, event_name, event_date, event_time)
VALUES 
    ('PR', 'Pradosha', '2025-12-08', '17:00:00'),
    ('PR', 'Pradosha', '2025-12-23', '17:05:00'),
    -- ... continue

-- Sankashta Chaturthi
INSERT INTO important_dates 
    (event_type, event_name, event_date, event_time)
VALUES 
    ('SK', 'Sankashta Chaturthi', '2025-12-18', '18:00:00'),
    ('SK', 'Sankashta Chaturthi', '2026-01-17', '18:10:00'),
    -- ... continue
```

## 3.2 Caching Strategy

For performance, pre-calculate and cache:

```python
# Redis cache structure
CACHE_KEY_PATTERN = "ready_reckoner:{event_type}:{date}"

# Example cache entries:
"ready_reckoner:NAK:2025-12-04" = {
    "today": {"name": "Krittika", "number": 3, "time": "10:00"},
    "next_5": [
        {"name": "Rohini", "date": "2025-12-10", "days_away": 6},
        {"name": "Rohini", "date": "2026-01-06", "days_away": 33},
        {"name": "Rohini", "date": "2026-02-02", "days_away": 60},
        {"name": "Rohini", "date": "2026-03-01", "days_away": 87},
        {"name": "Rohini", "date": "2026-03-28", "days_away": 114}
    ]
}

"ready_reckoner:EK:2025-12-04" = {
    "next_5": [
        {"name": "Utpanna Ekadashi", "date": "2025-12-07", "days_away": 3},
        {"name": "Mokshada Ekadashi", "date": "2025-12-21", "days_away": 17},
        {"name": "Saphala Ekadashi", "date": "2026-01-06", "days_away": 33},
        # ... etc
    ]
}
```

---

<a name="section-4"></a>
# 4. BACKEND IMPLEMENTATION (FastAPI)

## 4.1 File Structure

```
backend/
â"œâ"€â"€ app/
â"‚   â"œâ"€â"€ api/
â"‚   â"‚   â"œâ"€â"€ endpoints/
â"‚   â"‚   â"‚   â""â"€â"€ ready_reckoner.py    # New file
â"‚   â"‚   â""â"€â"€ __init__.py
â"‚   â"œâ"€â"€ services/
â"‚   â"‚   â"œâ"€â"€ panchang_service.py      # Existing
â"‚   â"‚   â""â"€â"€ ready_reckoner_service.py # New file
â"‚   â"œâ"€â"€ models/
â"‚   â"‚   â""â"€â"€ important_dates.py        # New file
â"‚   â""â"€â"€ __init__.py
â""â"€â"€ requirements.txt
```

## 4.2 Models (models/important_dates.py)

```python
"""
Models for Important Dates (Ready Reckoner)
"""
from datetime import date, time, datetime
from typing import Optional
from pydantic import BaseModel, Field

class ImportantDate(BaseModel):
    """Model for important date entry"""
    id: Optional[int] = None
    event_type: str = Field(..., description="NAK, EK, SK, PR, PM, AM")
    event_name: str = Field(..., description="Name in English")
    event_name_hindi: Optional[str] = Field(None, description="Name in Hindi")
    event_name_kannada: Optional[str] = Field(None, description="Name in Kannada")
    event_date: date
    event_time: Optional[time] = None
    end_time: Optional[time] = None
    hindu_month: Optional[str] = None
    paksha: Optional[str] = None  # 'Shukla' or 'Krishna'
    tithi_number: Optional[int] = None
    nakshatra_number: Optional[int] = None
    location_id: Optional[int] = None
    is_verified: bool = False
    
    class Config:
        orm_mode = True

class NextOccurrence(BaseModel):
    """Model for next occurrence of an event"""
    event_name: str
    event_name_hindi: Optional[str] = None
    event_name_kannada: Optional[str] = None
    event_date: date
    event_time: Optional[time] = None
    days_away: int
    day_of_week: str  # "Monday", "Tuesday", etc.
    hindu_month: Optional[str] = None
    paksha: Optional[str] = None
    is_today: bool = False
    
class ReadyReckonerResponse(BaseModel):
    """Response model for ready reckoner queries"""
    event_type: str
    query_date: date
    today_event: Optional[NextOccurrence] = None
    next_occurrences: list[NextOccurrence] = []
    total_found: int
    
class NakshatraFinderRequest(BaseModel):
    """Request to find next nakshatra dates"""
    nakshatra_name: str = Field(..., description="Name of nakshatra to find")
    limit: int = Field(default=5, description="Number of occurrences to return")
    start_date: Optional[date] = Field(None, description="Start searching from this date")
    
class NakshatraFinderResponse(BaseModel):
    """Response with nakshatra dates"""
    nakshatra_name: str
    nakshatra_number: int
    today_nakshatra: str
    is_today: bool
    next_occurrences: list[NextOccurrence]
```

## 4.3 Service Layer (services/ready_reckoner_service.py)

```python
"""
Ready Reckoner Service
Pre-calculates and caches important dates for quick lookup
"""
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.important_dates import ImportantDate, NextOccurrence, ReadyReckonerResponse
from app.services.panchang_service import PanchangService
import redis
import json

class ReadyReckonerService:
    """Service to provide quick lookups for important dates"""
    
    # 27 Nakshatras with multi-language names
    NAKSHATRAS = [
        {"num": 1, "en": "Ashwini", "hi": "à¤…à¤¶à¥à¤µà¤¿à¤¨à¥€", "ka": "à²…à²¶à³à²µà²¿à²¨à²¿"},
        {"num": 2, "en": "Bharani", "hi": "à¤­à¤°à¤£à¥€", "ka": "à²­à²°à²£à²¿"},
        {"num": 3, "en": "Krittika", "hi": "à¤•à¥ƒà¤¤à¥à¤¤à¤¿à¤•à¤¾", "ka": "à²•à³ƒà²¤à³à²¤à²¿à²•à³†"},
        {"num": 4, "en": "Rohini", "hi": "à¤°à¥‹à¤¹à¤¿à¤£à¥€", "ka": "à²°à³‹à²¹à²¿à²£à²¿"},
        {"num": 5, "en": "Mrigashira", "hi": "à¤®à¥ƒà¤—à¤¶à¤¿à¤°à¤¾", "ka": "à²®à³ƒà²—à²¶à²¿à²°"},
        {"num": 6, "en": "Ardra", "hi": "à¤†à¤°à¥à¤¦à¥à¤°à¤¾", "ka": "à²†à²°à³à²¦à³à²°"},
        {"num": 7, "en": "Punarvasu", "hi": "à¤ªà¥à¤¨à¤°à¥à¤µà¤¸à¥", "ka": "à²ªà³à²¨à²°à³à²µà²¸à³"},
        {"num": 8, "en": "Pushya", "hi": "à¤ªà¥à¤·à¥à¤¯", "ka": "à²ªà³à²·à³à²¯"},
        {"num": 9, "en": "Ashlesha", "hi": "à¤†à¤¶à¥à¤²à¥‡à¤·à¤¾", "ka": "à²†à²¶à³à²²à³‡à²·"},
        {"num": 10, "en": "Magha", "hi": "à¤®à¤˜à¤¾", "ka": "à²®à²˜"},
        {"num": 11, "en": "Purva Phalguni", "hi": "à¤ªà¥‚à¤°à¥à¤µà¤¾ à¤«à¤¾à¤²à¥à¤—à¥à¤¨à¥€", "ka": "à²ªà³‚à²°à³à²µ à²«à²¾à²²à³à²—à³à²¨à²¿"},
        {"num": 12, "en": "Uttara Phalguni", "hi": "à¤‰à¤¤à¥à¤¤à¤°à¤¾ à¤«à¤¾à¤²à¥à¤—à¥à¤¨à¥€", "ka": "à²‰à²¤à³à²¤à²° à²«à²¾à²²à³à²—à³à²¨à²¿"},
        {"num": 13, "en": "Hasta", "hi": "à¤¹à¤¸à¥à¤¤", "ka": "à²¹à²¸à³à²¤"},
        {"num": 14, "en": "Chitra", "hi": "à¤šà¤¿à¤¤à¥à¤°à¤¾", "ka": "à²šà²¿à²¤à³à²°"},
        {"num": 15, "en": "Swati", "hi": "à¤¸à¥à¤µà¤¾à¤¤à¤¿", "ka": "à²¸à³à²µà²¾à²¤à²¿"},
        {"num": 16, "en": "Vishakha", "hi": "à¤µà¤¿à¤¶à¤¾à¤–à¤¾", "ka": "à²µà²¿à²¶à²¾à²–"},
        {"num": 17, "en": "Anuradha", "hi": "à¤…à¤¨à¥à¤°à¤¾à¤§à¤¾", "ka": "à²…à²¨à³à²°à²¾à²§"},
        {"num": 18, "en": "Jyeshtha", "hi": "à¤œà¥à¤¯à¥‡à¤·à¥à¤ à¤¾", "ka": "à²œà³à²¯à³‡à²·à³à²Ÿ"},
        {"num": 19, "en": "Mula", "hi": "à¤®à¥‚à¤²", "ka": "à²®à³‚à²²"},
        {"num": 20, "en": "Purva Ashadha", "hi": "à¤ªà¥‚à¤°à¥à¤µà¤¾ à¤†à¤·à¤¾à¤¢à¤¼à¤¾", "ka": "à²ªà³‚à²°à³à²µ à²†à²·à²¾à²¢"},
        {"num": 21, "en": "Uttara Ashadha", "hi": "à¤‰à¤¤à¥à¤¤à¤°à¤¾ à¤†à¤·à¤¾à¤¢à¤¼à¤¾", "ka": "à²‰à²¤à³à²¤à²° à²†à²·à²¾à²¢"},
        {"num": 22, "en": "Shravana", "hi": "à¤¶à¥à¤°à¤µà¤£", "ka": "à²¶à³à²°à²µà²£"},
        {"num": 23, "en": "Dhanishta", "hi": "à¤§à¤¨à¤¿à¤·à¥à¤ à¤¾", "ka": "à²§à²¨à²¿à²·à³à²Ÿ"},
        {"num": 24, "en": "Shatabhisha", "hi": "à¤¶à¤¤à¤­à¤¿à¤·à¤¾", "ka": "à²¶à²¤à²­à²¿à²·"},
        {"num": 25, "en": "Purva Bhadrapada", "hi": "à¤ªà¥‚à¤°à¥à¤µà¤¾ à¤­à¤¾à¤¦à¥à¤°à¤ªà¤¦", "ka": "à²ªà³‚à²°à³à²µ à²­à²¾à²¦à³à²°à²ªà²¦"},
        {"num": 26, "en": "Uttara Bhadrapada", "hi": "à¤‰à¤¤à¥à¤¤à¤°à¤¾ à¤­à¤¾à¤¦à¥à¤°à¤ªà¤¦", "ka": "à²‰à²¤à³à²¤à²° à²­à²¾à²¦à³à²°à²ªà²¦"},
        {"num": 27, "en": "Revati", "hi": "à¤°à¥‡à¤µà¤¤à¥€", "ka": "à²°à³‡à²µà²¤à²¿"}
    ]
    
    def __init__(self, db: Session, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.panchang_service = PanchangService()
        
    # ========================================
    # CORE LOOKUP FUNCTIONS
    # ========================================
    
    def find_next_nakshatra(
        self, 
        nakshatra_name: str, 
        limit: int = 5,
        start_date: Optional[date] = None
    ) -> Dict:
        """
        Find next occurrences of a specific nakshatra
        
        Args:
            nakshatra_name: Name of nakshatra (e.g., "Rohini")
            limit: Number of occurrences to return
            start_date: Start searching from this date (default: today)
            
        Returns:
            Dict with today's nakshatra and next occurrences
        """
        if start_date is None:
            start_date = date.today()
            
        # Get nakshatra info
        nak_info = self._get_nakshatra_info(nakshatra_name)
        if not nak_info:
            raise ValueError(f"Invalid nakshatra name: {nakshatra_name}")
            
        # Check cache first
        cache_key = f"nak_finder:{nakshatra_name}:{start_date}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        # Get today's nakshatra
        today_panchang = self.panchang_service.get_daily_panchang(
            start_date,
            location=(12.97, 77.59)  # Bangalore, adjust as needed
        )
        today_nak_name = today_panchang['nakshatra']['name']
        
        # Find next occurrences
        next_occurrences = []
        current_date = start_date
        max_days = 365  # Search up to 1 year
        
        for _ in range(max_days):
            if len(next_occurrences) >= limit:
                break
                
            panchang = self.panchang_service.get_daily_panchang(
                current_date,
                location=(12.97, 77.59)
            )
            
            if panchang['nakshatra']['name'] == nakshatra_name:
                days_away = (current_date - start_date).days
                
                occurrence = NextOccurrence(
                    event_name=nakshatra_name,
                    event_name_hindi=nak_info['hi'],
                    event_name_kannada=nak_info['ka'],
                    event_date=current_date,
                    event_time=panchang['nakshatra'].get('start_time'),
                    days_away=days_away,
                    day_of_week=current_date.strftime('%A'),
                    is_today=(days_away == 0)
                )
                next_occurrences.append(occurrence)
                
            current_date += timedelta(days=1)
            
        result = {
            "nakshatra_name": nakshatra_name,
            "nakshatra_number": nak_info['num'],
            "today_nakshatra": today_nak_name,
            "is_today": (today_nak_name == nakshatra_name),
            "next_occurrences": next_occurrences
        }
        
        # Cache for 24 hours
        self._save_to_cache(cache_key, result, ttl=86400)
        
        return result
        
    def get_upcoming_important_dates(
        self,
        event_type: Optional[str] = None,
        limit: int = 10,
        start_date: Optional[date] = None
    ) -> ReadyReckonerResponse:
        """
        Get upcoming important dates for dashboard display
        
        Args:
            event_type: Type of event (NAK, EK, SK, PR, PM, AM) or None for all
            limit: Number of dates to return
            start_date: Start from this date (default: today)
            
        Returns:
            ReadyReckonerResponse with upcoming dates
        """
        if start_date is None:
            start_date = date.today()
            
        # Check cache
        cache_key = f"upcoming:{event_type or 'all'}:{start_date}:{limit}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return ReadyReckonerResponse(**cached)
            
        # Query database
        query = self.db.query(ImportantDate)
        query = query.filter(ImportantDate.event_date >= start_date)
        
        if event_type:
            query = query.filter(ImportantDate.event_type == event_type)
            
        query = query.order_by(ImportantDate.event_date)
        query = query.limit(limit)
        
        dates = query.all()
        
        # Convert to NextOccurrence objects
        occurrences = []
        for d in dates:
            days_away = (d.event_date - start_date).days
            
            occurrence = NextOccurrence(
                event_name=d.event_name,
                event_name_hindi=d.event_name_hindi,
                event_name_kannada=d.event_name_kannada,
                event_date=d.event_date,
                event_time=d.event_time,
                days_away=days_away,
                day_of_week=d.event_date.strftime('%A'),
                hindu_month=d.hindu_month,
                paksha=d.paksha,
                is_today=(days_away == 0)
            )
            occurrences.append(occurrence)
            
        result = ReadyReckonerResponse(
            event_type=event_type or "ALL",
            query_date=start_date,
            next_occurrences=occurrences,
            total_found=len(occurrences)
        )
        
        # Cache for 24 hours
        self._save_to_cache(cache_key, result.dict(), ttl=86400)
        
        return result
        
    # ========================================
    # PRE-CALCULATION FUNCTIONS
    # ========================================
    
    def pre_calculate_dates(
        self,
        start_date: date,
        end_date: date,
        location: tuple = (12.97, 77.59)
    ):
        """
        Pre-calculate important dates for a date range
        This should be run daily via cron job
        
        Args:
            start_date: Start date for calculations
            end_date: End date for calculations
            location: (lat, lon) tuple for location
        """
        print(f"Pre-calculating dates from {start_date} to {end_date}")
        
        current_date = start_date
        batch_size = 100
        batch = []
        
        while current_date <= end_date:
            # Get panchang for this date
            panchang = self.panchang_service.get_daily_panchang(
                current_date,
                location
            )
            
            # Extract important dates
            important_dates = self._extract_important_dates(
                current_date,
                panchang
            )
            
            batch.extend(important_dates)
            
            # Bulk insert every 100 records
            if len(batch) >= batch_size:
                self._bulk_insert_dates(batch)
                batch = []
                
            current_date += timedelta(days=1)
            
        # Insert remaining
        if batch:
            self._bulk_insert_dates(batch)
            
        print(f"Pre-calculation complete. Calculated {(end_date - start_date).days + 1} days")
        
    def _extract_important_dates(
        self,
        current_date: date,
        panchang: Dict
    ) -> List[ImportantDate]:
        """Extract important dates from daily panchang"""
        important_dates = []
        
        # Nakshatra
        nak = panchang['nakshatra']
        nak_info = self._get_nakshatra_info(nak['name'])
        
        important_dates.append(ImportantDate(
            event_type='NAK',
            event_name=nak['name'],
            event_name_hindi=nak_info['hi'] if nak_info else None,
            event_name_kannada=nak_info['ka'] if nak_info else None,
            event_date=current_date,
            event_time=nak.get('start_time'),
            end_time=nak.get('end_time'),
            nakshatra_number=nak_info['num'] if nak_info else None
        ))
        
        # Ekadashi (if today is Ekadashi)
        tithi = panchang['tithi']
        if tithi['number'] == 11:  # Ekadashi
            important_dates.append(ImportantDate(
                event_type='EK',
                event_name=f"{tithi['paksha']} Ekadashi",
                event_date=current_date,
                event_time=tithi.get('start_time'),
                hindu_month=panchang.get('hindu_month'),
                paksha=tithi['paksha'],
                tithi_number=11
            ))
            
        # Sankashta Chaturthi (Krishna Paksha Chaturthi)
        if tithi['number'] == 4 and tithi['paksha'] == 'Krishna':
            important_dates.append(ImportantDate(
                event_type='SK',
                event_name='Sankashta Chaturthi',
                event_date=current_date,
                event_time=tithi.get('start_time'),
                hindu_month=panchang.get('hindu_month'),
                paksha='Krishna',
                tithi_number=4
            ))
            
        # Pradosha (Trayodashi)
        if tithi['number'] == 13:
            important_dates.append(ImportantDate(
                event_type='PR',
                event_name=f"{tithi['paksha']} Pradosha",
                event_date=current_date,
                event_time=tithi.get('start_time'),
                hindu_month=panchang.get('hindu_month'),
                paksha=tithi['paksha'],
                tithi_number=13
            ))
            
        # Pournami (Full Moon)
        if tithi['number'] == 15 and tithi['paksha'] == 'Shukla':
            important_dates.append(ImportantDate(
                event_type='PM',
                event_name='Pournami',
                event_date=current_date,
                event_time=tithi.get('start_time'),
                hindu_month=panchang.get('hindu_month'),
                paksha='Shukla',
                tithi_number=15
            ))
            
        # Amavasya (New Moon)
        if tithi['number'] == 30:  # or could be 0 depending on system
            important_dates.append(ImportantDate(
                event_type='AM',
                event_name='Amavasya',
                event_date=current_date,
                event_time=tithi.get('start_time'),
                hindu_month=panchang.get('hindu_month'),
                paksha='Krishna',
                tithi_number=30
            ))
            
        return important_dates
        
    # ========================================
    # HELPER FUNCTIONS
    # ========================================
    
    def _get_nakshatra_info(self, name: str) -> Optional[Dict]:
        """Get nakshatra info by name"""
        for nak in self.NAKSHATRAS:
            if nak['en'].lower() == name.lower():
                return nak
        return None
        
    def _bulk_insert_dates(self, dates: List[ImportantDate]):
        """Bulk insert dates into database"""
        # Convert to dicts
        date_dicts = [d.dict(exclude={'id'}) for d in dates]
        
        # Insert
        self.db.bulk_insert_mappings(ImportantDate, date_dicts)
        self.db.commit()
        
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from Redis cache"""
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
        
    def _save_to_cache(self, key: str, data: Dict, ttl: int = 3600):
        """Save data to Redis cache"""
        try:
            self.redis.setex(
                key,
                ttl,
                json.dumps(data, default=str)
            )
        except Exception as e:
            print(f"Cache save error: {e}")
```

## 4.4 API Endpoints (api/endpoints/ready_reckoner.py)

```python
"""
Ready Reckoner API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional

from app.services.ready_reckoner_service import ReadyReckonerService
from app.models.important_dates import (
    NakshatraFinderRequest,
    NakshatraFinderResponse,
    ReadyReckonerResponse
)
from app.database import get_db
from app.cache import get_redis

router = APIRouter(prefix="/api/ready-reckoner", tags=["Ready Reckoner"])

@router.get("/nakshatra/{nakshatra_name}", response_model=NakshatraFinderResponse)
async def find_nakshatra_dates(
    nakshatra_name: str,
    limit: int = Query(default=5, ge=1, le=20),
    start_date: Optional[date] = None,
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Find next occurrences of a specific nakshatra
    
    **Example:**
    ```
    GET /api/ready-reckoner/nakshatra/Rohini?limit=5
    ```
    
    **Response:**
    ```json
    {
        "nakshatra_name": "Rohini",
        "nakshatra_number": 4,
        "today_nakshatra": "Krittika",
        "is_today": false,
        "next_occurrences": [
            {
                "event_name": "Rohini",
                "event_date": "2025-12-10",
                "days_away": 6,
                "day_of_week": "Tuesday"
            },
            ...
        ]
    }
    ```
    """
    service = ReadyReckonerService(db, redis)
    
    try:
        result = service.find_next_nakshatra(
            nakshatra_name=nakshatra_name,
            limit=limit,
            start_date=start_date
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/upcoming/{event_type}", response_model=ReadyReckonerResponse)
async def get_upcoming_dates(
    event_type: str,
    limit: int = Query(default=10, ge=1, le=50),
    start_date: Optional[date] = None,
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Get upcoming dates for specific event type
    
    **Event Types:**
    - `NAK`: Nakshatras
    - `EK`: Ekadashi
    - `SK`: Sankashta Chaturthi
    - `PR`: Pradosha
    - `PM`: Pournami
    - `AM`: Amavasya
    
    **Example:**
    ```
    GET /api/ready-reckoner/upcoming/EK?limit=10
    ```
    """
    valid_types = ['NAK', 'EK', 'SK', 'PR', 'PM', 'AM']
    if event_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event type. Must be one of: {', '.join(valid_types)}"
        )
        
    service = ReadyReckonerService(db, redis)
    
    result = service.get_upcoming_important_dates(
        event_type=event_type,
        limit=limit,
        start_date=start_date
    )
    return result

@router.get("/dashboard", response_model=Dict)
async def get_dashboard_data(
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Get complete dashboard data with all upcoming important dates
    
    Returns next 5 occurrences of each event type
    
    **Example:**
    ```
    GET /api/ready-reckoner/dashboard
    ```
    
    **Response:**
    ```json
    {
        "today": "2025-12-04",
        "current_nakshatra": "Krittika",
        "upcoming": {
            "ekadashi": [...],
            "pradosha": [...],
            "sankashta": [...],
            "pournami": [...],
            "amavasya": [...]
        }
    }
    ```
    """
    service = ReadyReckonerService(db, redis)
    today = date.today()
    
    # Get today's panchang for current nakshatra
    panchang = service.panchang_service.get_daily_panchang(
        today,
        location=(12.97, 77.59)
    )
    
    # Get upcoming dates for each event type
    result = {
        "today": today,
        "current_nakshatra": panchang['nakshatra']['name'],
        "upcoming": {}
    }
    
    for event_type in ['EK', 'PR', 'SK', 'PM', 'AM']:
        data = service.get_upcoming_important_dates(
            event_type=event_type,
            limit=5
        )
        result["upcoming"][event_type.lower()] = data.next_occurrences
        
    return result

@router.post("/pre-calculate")
async def trigger_pre_calculation(
    days_ahead: int = Query(default=365, ge=1, le=730),
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Trigger pre-calculation of important dates
    
    **Admin only** - Should be called via cron job daily
    
    **Example:**
    ```
    POST /api/ready-reckoner/pre-calculate?days_ahead=365
    ```
    """
    service = ReadyReckonerService(db, redis)
    
    start_date = date.today()
    end_date = start_date + timedelta(days=days_ahead)
    
    # This should run in background task in production
    service.pre_calculate_dates(
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "status": "success",
        "message": f"Pre-calculated {days_ahead} days",
        "start_date": start_date,
        "end_date": end_date
    }
```

---

<a name="section-5"></a>
# 5. FRONTEND WIDGET (React)

## 5.1 Component Structure

```
frontend/
â"œâ"€â"€ src/
â"‚   â"œâ"€â"€ components/
â"‚   â"‚   â"œâ"€â"€ ReadyReckoner/
â"‚   â"‚   â"‚   â"œâ"€â"€ ReadyReckonerWidget.jsx       # Main widget
â"‚   â"‚   â"‚   â"œâ"€â"€ NakshatraFinder.jsx          # Star finder
â"‚   â"‚   â"‚   â"œâ"€â"€ UpcomingDates.jsx            # Upcoming dates
â"‚   â"‚   â"‚   â"œâ"€â"€ EventTypeSelector.jsx        # Event dropdown
â"‚   â"‚   â"‚   â""â"€â"€ ReadyReckoner.css            # Styles
â"‚   â"‚   â""â"€â"€ ...
â"‚   â"œâ"€â"€ services/
â"‚   â"‚   â""â"€â"€ readyReckonerService.js          # API calls
â"‚   â""â"€â"€ ...
```

## 5.2 Main Widget Component (ReadyReckonerWidget.jsx)

```jsx
/**
 * Ready Reckoner Widget
 * Quick reference for important dates
 */
import React, { useState, useEffect } from 'react';
import { Card, Tabs, Tab, Box, Typography } from '@mui/material';
import NakshatraFinder from './NakshatraFinder';
import UpcomingDates from './UpcomingDates';
import EventTypeSelector from './EventTypeSelector';
import { readyReckonerService } from '../../services/readyReckonerService';
import './ReadyReckoner.css';

const ReadyReckonerWidget = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState(0);
  
  useEffect(() => {
    loadDashboardData();
    
    // Refresh every midnight
    const midnight = new Date();
    midnight.setHours(24, 0, 0, 0);
    const msUntilMidnight = midnight - new Date();
    
    const timer = setTimeout(() => {
      loadDashboardData();
      // Set daily refresh
      setInterval(loadDashboardData, 24 * 60 * 60 * 1000);
    }, msUntilMidnight);
    
    return () => clearTimeout(timer);
  }, []);
  
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const data = await readyReckonerService.getDashboardData();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };
  
  if (loading) {
    return (
      <Card className="ready-reckoner-widget loading">
        <Typography>Loading...</Typography>
      </Card>
    );
  }
  
  return (
    <Card className="ready-reckoner-widget">
      <Box className="widget-header">
        <Typography variant="h5">
          ðŸ"… Devotee Ready Reckoner
        </Typography>
        <Typography variant="subtitle2" color="textSecondary">
          Quick reference for important dates
        </Typography>
      </Box>
      
      <Box className="current-info">
        <Typography variant="body2">
          <strong>Today:</strong> {new Date(dashboardData.today).toLocaleDateString('en-IN', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
        </Typography>
        <Typography variant="body2">
          <strong>Current Star:</strong> {dashboardData.current_nakshatra}
        </Typography>
      </Box>
      
      <Tabs value={selectedTab} onChange={handleTabChange}>
        <Tab label="Find Star" />
        <Tab label="Upcoming Dates" />
        <Tab label="All Events" />
      </Tabs>
      
      <Box className="tab-content">
        {selectedTab === 0 && (
          <NakshatraFinder currentNakshatra={dashboardData.current_nakshatra} />
        )}
        
        {selectedTab === 1 && (
          <UpcomingDates upcomingData={dashboardData.upcoming} />
        )}
        
        {selectedTab === 2 && (
          <EventTypeSelector />
        )}
      </Box>
    </Card>
  );
};

export default ReadyReckonerWidget;
```

## 5.3 Nakshatra Finder Component

```jsx
/**
 * Nakshatra Finder
 * Find dates for specific birth star
 */
import React, { useState } from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress
} from '@mui/material';
import { Search as SearchIcon, Star as StarIcon } from '@mui/icons-material';
import { readyReckonerService } from '../../services/readyReckonerService';

const NAKSHATRAS = [
  { en: "Ashwini", hi: "à¤…à¤¶à¥à¤µà¤¿à¤¨à¥€", ka: "à²…à²¶à³à²µà²¿à²¨à²¿" },
  { en: "Bharani", hi: "à¤­à¤°à¤£à¥€", ka: "à²­à²°à²£à²¿" },
  { en: "Krittika", hi: "à¤•à¥ƒà¤¤à¥à¤¤à¤¿à¤•à¤¾", ka: "à²•à³ƒà²¤à³à²¤à²¿à²•à³†" },
  { en: "Rohini", hi: "à¤°à¥‹à¤¹à¤¿à¤£à¥€", ka: "à²°à³‹à²¹à²¿à²£à²¿" },
  { en: "Mrigashira", hi: "à¤®à¥ƒà¤—à¤¶à¤¿à¤°à¤¾", ka: "à²®à³ƒà²—à²¶à²¿à²°" },
  // ... all 27 nakshatras
];

const NakshatraFinder = ({ currentNakshatra }) => {
  const [selectedNakshatra, setSelectedNakshatra] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState('en'); // 'en', 'hi', 'ka'
  
  const handleFind = async () => {
    if (!selectedNakshatra) return;
    
    try {
      setLoading(true);
      const data = await readyReckonerService.findNakshatra(selectedNakshatra, 5);
      setResults(data);
    } catch (error) {
      console.error('Failed to find nakshatra:', error);
      alert('Failed to find dates. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleBook = (date) => {
    // Integrate with seva booking
    console.log('Book seva for date:', date);
    // Navigate to booking page or open booking modal
  };
  
  return (
    <Box className="nakshatra-finder">
      <Box className="finder-controls">
        <FormControl fullWidth>
          <InputLabel>Select Birth Star</InputLabel>
          <Select
            value={selectedNakshatra}
            onChange={(e) => setSelectedNakshatra(e.target.value)}
            label="Select Birth Star"
          >
            {NAKSHATRAS.map((nak) => (
              <MenuItem key={nak.en} value={nak.en}>
                {nak.en} ({nak.hi})
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <Button
          variant="contained"
          startIcon={<SearchIcon />}
          onClick={handleFind}
          disabled={!selectedNakshatra || loading}
          fullWidth
          sx={{ mt: 2 }}
        >
          {loading ? <CircularProgress size={24} /> : 'Find Dates'}
        </Button>
      </Box>
      
      {results && (
        <Box className="finder-results" sx={{ mt: 3 }}>
          <Box className="result-header">
            <Typography variant="h6">
              <StarIcon /> {results.nakshatra_name}
            </Typography>
            
            {results.is_today ? (
              <Chip
                label="Today is this star!"
                color="success"
                size="small"
              />
            ) : (
              <Typography variant="body2" color="textSecondary">
                Today's star: {results.today_nakshatra}
              </Typography>
            )}
          </Box>
          
          <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
            Next Occurrences:
          </Typography>
          
          <List>
            {results.next_occurrences.map((occurrence, index) => (
              <ListItem
                key={index}
                className="occurrence-item"
                secondaryAction={
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => handleBook(occurrence.event_date)}
                  >
                    Book Seva
                  </Button>
                }
              >
                <ListItemText
                  primary={
                    <>
                      <strong>
                        {new Date(occurrence.event_date).toLocaleDateString('en-IN', {
                          weekday: 'long',
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </strong>
                      {occurrence.is_today && (
                        <Chip label="TODAY" size="small" color="primary" sx={{ ml: 1 }} />
                      )}
                    </>
                  }
                  secondary={
                    <>
                      In {occurrence.days_away} days
                      {occurrence.event_time && ` â€¢ Starts at ${occurrence.event_time}`}
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>
          
          <Box className="result-actions" sx={{ mt: 2 }}>
            <Button variant="text" size="small">
              View Full Calendar
            </Button>
            <Button variant="text" size="small">
              Print Reference
            </Button>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default NakshatraFinder;
```

## 5.4 Upcoming Dates Component

```jsx
/**
 * Upcoming Important Dates
 * Dashboard display of upcoming events
 */
import React from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Chip
} from '@mui/material';
import {
  Star as EkadashiIcon,
  Brightness2 as PradoshaIcon,
  TripOrigin as SankhastaIcon,
  Brightness5 as PournamiIcon,
  Brightness4 as AmavasyaIcon
} from '@mui/icons-material';

const EVENT_CONFIG = {
  ek: {
    icon: EkadashiIcon,
    label: 'Ekadashi',
    color: '#4CAF50'
  },
  pr: {
    icon: PradoshaIcon,
    label: 'Pradosha',
    color: '#2196F3'
  },
  sk: {
    icon: SankhastaIcon,
    label: 'Sankashta Chaturthi',
    color: '#FF9800'
  },
  pm: {
    icon: PournamiIcon,
    label: 'Pournami',
    color: '#FFC107'
  },
  am: {
    icon: AmavasyaIcon,
    label: 'Amavasya',
    color: '#9E9E9E'
  }
};

const UpcomingDates = ({ upcomingData }) => {
  const renderEventGroup = (eventType, occurrences) => {
    const config = EVENT_CONFIG[eventType];
    const Icon = config.icon;
    
    if (!occurrences || occurrences.length === 0) {
      return null;
    }
    
    return (
      <Box key={eventType} className="event-group" sx={{ mb: 2 }}>
        <Typography variant="subtitle1" sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
          <Icon sx={{ mr: 1, color: config.color }} />
          {config.label}
        </Typography>
        
        <List dense>
          {occurrences.slice(0, 2).map((occurrence, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={
                  <>
                    {occurrence.event_name}
                    {occurrence.is_today && (
                      <Chip label="TODAY" size="small" color="primary" sx={{ ml: 1 }} />
                    )}
                  </>
                }
                secondary={
                  <>
                    {new Date(occurrence.event_date).toLocaleDateString('en-IN', {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric'
                    })}
                    {' â€¢ '}
                    {occurrence.days_away === 0 ? 'Today' : 
                     occurrence.days_away === 1 ? 'Tomorrow' :
                     `In ${occurrence.days_away} days`}
                  </>
                }
              />
            </ListItem>
          ))}
        </List>
        
        <Divider sx={{ mt: 1 }} />
      </Box>
    );
  };
  
  return (
    <Box className="upcoming-dates">
      <Typography variant="h6" sx={{ mb: 2 }}>
        ðŸ"† Upcoming Important Dates
      </Typography>
      
      {Object.entries(upcomingData).map(([eventType, occurrences]) =>
        renderEventGroup(eventType, occurrences)
      )}
      
      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Button variant="outlined" fullWidth>
          View Full Calendar
        </Button>
      </Box>
    </Box>
  );
};

export default UpcomingDates;
```

## 5.5 API Service (services/readyReckonerService.js)

```javascript
/**
 * Ready Reckoner API Service
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ReadyReckonerService {
  /**
   * Get dashboard data with all upcoming dates
   */
  async getDashboardData() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/ready-reckoner/dashboard`);
      return response.data;
    } catch (error) {
      console.error('Failed to get dashboard data:', error);
      throw error;
    }
  }
  
  /**
   * Find next occurrences of a nakshatra
   */
  async findNakshatra(nakshatraName, limit = 5) {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/ready-reckoner/nakshatra/${nakshatraName}`,
        { params: { limit } }
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to find ${nakshatraName}:`, error);
      throw error;
    }
  }
  
  /**
   * Get upcoming dates for specific event type
   */
  async getUpcomingDates(eventType, limit = 10) {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/ready-reckoner/upcoming/${eventType}`,
        { params: { limit } }
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to get upcoming ${eventType}:`, error);
      throw error;
    }
  }
  
  /**
   * Trigger pre-calculation (admin only)
   */
  async triggerPreCalculation(daysAhead = 365) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/ready-reckoner/pre-calculate`,
        null,
        { params: { days_ahead: daysAhead } }
      );
      return response.data;
    } catch (error) {
      console.error('Failed to trigger pre-calculation:', error);
      throw error;
    }
  }
}

export const readyReckonerService = new ReadyReckonerService();
```

---

<a name="section-6"></a>
# 6. INTEGRATION WITH EXISTING PANCHANG

## 6.1 How It Works Together

```
                    MandirMitra ARCHITECTURE
                              
   â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
   â"‚        EXISTING PANCHANG SERVICE           â"‚
   â"‚                                            â"‚
   â"‚  - Daily panchang calculations             â"‚
   â"‚  - Tithi, Nakshatra, Yoga, Karana         â"‚
   â"‚  - Rahu Kaal, Abhijit Muhurat              â"‚
   â"‚  - Swiss Ephemeris integration             â"‚
   â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"¬â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
             â"‚
             â"‚ Uses â‡"
             â"‚
   â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"´â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
   â"‚      NEW READY RECKONER SERVICE           â"‚
   â"‚                                            â"‚
   â"‚  - Pre-calculates important dates          â"‚
   â"‚  - Stores in database for fast lookup      â"‚
   â"‚  - Caches frequently accessed data         â"‚
   â"‚  - Provides quick search APIs              â"‚
   â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"¬â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
                â"‚
                â"‚ Serves
                â"‚
   â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"´â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
   â"‚       DASHBOARD WIDGET (React)            â"‚
   â"‚                                            â"‚
   â"‚  - Star finder interface                   â"‚
   â"‚  - Upcoming dates display                  â"‚
   â"‚  - Quick booking integration               â"‚
   â"‚  - Print reference sheets                  â"‚
   â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
```

## 6.2 Daily Update Flow

```python
# Daily cron job (runs at midnight)
# Add to your crontab:
# 0 0 * * * python /path/to/update_ready_reckoner.py

"""
Daily update script for Ready Reckoner
Runs at midnight to pre-calculate next 365 days
"""
import sys
sys.path.append('/path/to/MandirMitra/backend')

from datetime import date, timedelta
from app.database import SessionLocal
from app.cache import RedisClient
from app.services.ready_reckoner_service import ReadyReckonerService

def main():
    db = SessionLocal()
    redis = RedisClient()
    service = ReadyReckonerService(db, redis)
    
    # Calculate for next 365 days
    start = date.today()
    end = start + timedelta(days=365)
    
    print(f"Starting pre-calculation from {start} to {end}")
    
    try:
        service.pre_calculate_dates(
            start_date=start,
            end_date=end
        )
        print("Pre-calculation completed successfully")
    except Exception as e:
        print(f"Error during pre-calculation: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
```

---

<a name="section-7"></a>
# 7. STEP-BY-STEP BUILD GUIDE (For Beginners)

## Step 1: Database Setup (Week 1, Day 1-2)

### What to Do:

1. **Create migration file:**

```bash
# In terminal
cd backend
alembic revision -m "create_important_dates_table"
```

2. **Write migration:**

```python
# In migration file (auto-generated in alembic/versions/)

def upgrade():
    op.create_table(
        'important_dates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=10), nullable=False),
        sa.Column('event_name', sa.String(length=100), nullable=True),
        sa.Column('event_name_hindi', sa.String(length=100), nullable=True),
        sa.Column('event_name_kannada', sa.String(length=100), nullable=True),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('event_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('hindu_month', sa.String(length=50), nullable=True),
        sa.Column('paksha', sa.String(length=20), nullable=True),
        sa.Column('tithi_number', sa.Integer(), nullable=True),
        sa.Column('nakshatra_number', sa.Integer(), nullable=True),
        sa.Column('location_id', sa.Integer(), nullable=True),
        sa.Column('calculated_date', sa.DateTime(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_event_type', 'important_dates', ['event_type'])
    op.create_index('idx_event_date', 'important_dates', ['event_date'])
    op.create_index('idx_nakshatra_number', 'important_dates', ['nakshatra_number'])
    op.create_index('idx_combined', 'important_dates', ['event_type', 'event_date'])

def downgrade():
    op.drop_index('idx_combined', table_name='important_dates')
    op.drop_index('idx_nakshatra_number', table_name='important_dates')
    op.drop_index('idx_event_date', table_name='important_dates')
    op.drop_index('idx_event_type', table_name='important_dates')
    op.drop_table('important_dates')
```

3. **Run migration:**

```bash
alembic upgrade head
```

**âœ… Checkpoint:** You should see the `important_dates` table in your database

## Step 2: Create Models (Week 1, Day 3)

**Copy the models code from Section 4.2 into:**
`backend/app/models/important_dates.py`

**âœ… Checkpoint:** File created, no syntax errors

## Step 3: Create Service (Week 1, Day 4-5)

**Copy the service code from Section 4.3 into:**
`backend/app/services/ready_reckoner_service.py`

**âœ… Checkpoint:** File created, imports work

## Step 4: Create API Endpoints (Week 2, Day 1-2)

**Copy the endpoint code from Section 4.4 into:**
`backend/app/api/endpoints/ready_reckoner.py`

**Register endpoints in main app:**

```python
# In backend/app/main.py

from app.api.endpoints import ready_reckoner

app.include_router(ready_reckoner.router)
```

**Test endpoints:**

```bash
# Start backend
uvicorn app.main:app --reload

# In another terminal, test
curl http://localhost:8000/api/ready-reckoner/dashboard
```

**âœ… Checkpoint:** API returns JSON data

## Step 5: Pre-Calculate Initial Data (Week 2, Day 3)

**Run pre-calculation:**

```bash
# Using curl or Postman
POST http://localhost:8000/api/ready-reckoner/pre-calculate?days_ahead=365
```

This will take 5-10 minutes. Watch console output.

**âœ… Checkpoint:** Database has ~6,570 records (365 days Ã— ~18 events/day)

## Step 6: Create Frontend Service (Week 2, Day 4)

**Copy the service code from Section 5.5 into:**
`frontend/src/services/readyReckonerService.js`

**âœ… Checkpoint:** File created, no syntax errors

## Step 7: Create React Components (Week 2, Day 5 - Week 3, Day 2)

**Create component files:**

1. `frontend/src/components/ReadyReckoner/ReadyReckonerWidget.jsx`
2. `frontend/src/components/ReadyReckoner/NakshatraFinder.jsx`
3. `frontend/src/components/ReadyReckoner/UpcomingDates.jsx`

**Copy code from Section 5.2, 5.3, 5.4**

**âœ… Checkpoint:** Components render without errors

## Step 8: Add Widget to Dashboard (Week 3, Day 3)

```jsx
// In your main Dashboard.jsx

import ReadyReckonerWidget from './components/ReadyReckoner/ReadyReckonerWidget';

// In render:
<Grid container spacing={3}>
  <Grid item xs={12} md={6}>
    <ReadyReckonerWidget />
  </Grid>
  {/* ... other widgets ... */}
</Grid>
```

**âœ… Checkpoint:** Widget appears on dashboard

## Step 9: Test & Verify (Week 3, Day 4-5)

**Test all features:**

- [ ] Nakshatra finder works
- [ ] Shows correct "days away"
- [ ] Upcoming dates load
- [ ] All event types work
- [ ] Multi-language names display
- [ ] Booking integration works
- [ ] Print functionality works

## Step 10: Setup Cron Job (Week 3, Day 5)

```bash
# Add to crontab
crontab -e

# Add this line:
0 0 * * * /path/to/python /path/to/update_ready_reckoner.py >> /var/log/ready_reckoner.log 2>&1
```

**âœ… Checkpoint:** Data auto-updates daily

---

<a name="section-8"></a>
# 8. TESTING & VERIFICATION

## 8.1 Test Cases

### Test Case 1: Nakshatra Finder

```
GIVEN: User selects "Rohini" nakshatra
WHEN: User clicks "Find Dates"
THEN:
  - API call succeeds
  - Shows current nakshatra
  - Shows next 5 Rohini dates
  - Days away calculated correctly
  - Dates are in ascending order
```

### Test Case 2: Today's Date

```
GIVEN: Today is Ekadashi
WHEN: Dashboard loads
THEN:
  - "Today" chip appears on Ekadashi entry
  - days_away = 0
  - is_today = true
```

### Test Case 3: Multi-Language

```
GIVEN: User selects Kannada language
WHEN: Viewing nakshatra names
THEN:
  - Names display in Kannada script
  - Fallback to English if translation missing
```

## 8.2 Performance Benchmarks

| Operation | Target | Acceptable |
|-----------|--------|------------|
| Dashboard load | < 200ms | < 500ms |
| Nakshatra search | < 100ms | < 300ms |
| Pre-calculation (365 days) | < 5 min | < 10 min |

## 8.3 Accuracy Verification

**Cross-check with authoritative sources:**

1. **Drik Panchang:** www.drikpanchang.com
2. **ProKerala:** www.prokerala.com
3. **Physical panchang book**

**Verify 10 random dates** - must match 100%!

---

<a name="section-9"></a>
# 9. CURSOR AI PROMPTS

## 9.1 Initial Setup Prompt

```
I need to build a "Devotee Ready Reckoner" widget for MandirMitra temple software.

REQUIREMENTS:
1. Backend: FastAPI + PostgreSQL + Redis
2. Frontend: React + Material-UI
3. Features:
   - Find next dates for any nakshatra (birth star)
   - Display upcoming Ekadashi, Pradosha, Sankashta dates
   - Quick lookup for counter clerks
   - Pre-calculate dates for performance

CONTEXT:
- We already have a working Panchang service that calculates daily panchang
- This new service will pre-calculate and store important dates
- Need database table, service layer, API endpoints, React components

ARCHITECTURE:
```
PanchangService (existing)
    â†"
ReadyReckonerService (new) â†' Pre-calculates dates
    â†"
Database (important_dates table)
    â†"
API Endpoints
    â†"
React Widget
```

START WITH:
1. Create database migration for important_dates table
2. Then create Pydantic models

Use the file structure from the implementation guide I'll provide.
```

## 9.2 Database Setup Prompt

```
Create database migration for Ready Reckoner feature.

TABLE: important_dates

COLUMNS:
- id (primary key)
- event_type (VARCHAR: 'NAK', 'EK', 'SK', 'PR', 'PM', 'AM')
- event_name (VARCHAR: English name)
- event_name_hindi, event_name_kannada (VARCHAR: translations)
- event_date (DATE: when event occurs)
- event_time, end_time (TIME: start/end times)
- hindu_month, paksha (VARCHAR: Hindu calendar info)
- tithi_number, nakshatra_number (INT: reference numbers)
- location_id (INT: for multi-location)
- calculated_date (TIMESTAMP: when calculated)
- is_verified (BOOLEAN: pandit verified)

INDEXES:
- event_type
- event_date  
- nakshatra_number
- Combined (event_type, event_date)

Use Alembic migration. Create both upgrade() and downgrade().
```

## 9.3 Service Implementation Prompt

```
Implement ReadyReckonerService class.

DEPENDENCIES:
- Existing PanchangService (for calculations)
- Database session (SQLAlchemy)
- Redis (for caching)

KEY METHODS:
1. find_next_nakshatra(nakshatra_name, limit=5)
   - Find next X occurrences of a nakshatra
   - Use existing PanchangService to calculate
   - Return list of dates with days_away

2. get_upcoming_important_dates(event_type, limit=10)
   - Query database for upcoming dates
   - Filter by event_type (EK, PR, SK, etc.)
   - Return with days remaining

3. pre_calculate_dates(start_date, end_date)
   - Loop through date range
   - Get daily panchang for each date
   - Extract important dates (Ekadashi, Pradosha, etc.)
   - Bulk insert to database
   - This runs via cron job

CACHING:
- Cache nakshatra searches for 24 hours
- Cache dashboard data for 1 hour
- Use Redis keys like: "nak_finder:Rohini:2025-12-04"

Follow the implementation from the guide.
```

## 9.4 API Endpoints Prompt

```
Create FastAPI endpoints for Ready Reckoner.

ROUTES:
1. GET /api/ready-reckoner/nakshatra/{name}
   - Query params: limit, start_date
   - Returns: NakshatraFinderResponse
   - Calls service.find_next_nakshatra()

2. GET /api/ready-reckoner/upcoming/{event_type}
   - Query params: limit, start_date
   - Validates event_type in ['NAK', 'EK', 'SK', 'PR', 'PM', 'AM']
   - Returns: ReadyReckonerResponse

3. GET /api/ready-reckoner/dashboard
   - No params
   - Returns all upcoming dates for all event types
   - Used by main dashboard widget

4. POST /api/ready-reckoner/pre-calculate
   - Admin only
   - Query param: days_ahead (default 365)
   - Triggers pre-calculation
   - Should run async in production

Add proper error handling, validation, and OpenAPI docs.
```

## 9.5 React Widget Prompt

```
Create React component: ReadyReckonerWidget

FEATURES:
1. Tab interface:
   - "Find Star" - nakshatra finder
   - "Upcoming Dates" - all upcoming important dates
   - "All Events" - filtered by event type

2. Nakshatra Finder tab:
   - Dropdown with all 27 nakshatras
   - Search button
   - Results display:
     * Today's current nakshatra
     * Next 5 occurrences with dates
     * "Days away" counter
     * "Book Seva" button for each date

3. Upcoming Dates tab:
   - Grouped by event type
   - Shows next 2 occurrences per type
   - Color-coded icons
   - "View Full Calendar" link

4. Auto-refresh at midnight
5. Loading states
6. Error handling

Use Material-UI components. Follow the design from the guide.
```

## 9.6 Testing Prompt

```
Create tests for Ready Reckoner feature.

BACKEND TESTS:
1. test_find_nakshatra()
   - Mock PanchangService
   - Verify correct dates returned
   - Check days_away calculation
   - Verify caching works

2. test_pre_calculate_dates()
   - Calculate 30 days
   - Verify database has ~540 records (30 Ã— 18)
   - Check all event types present
   - Verify dates in sequence

3. test_api_endpoints()
   - Test all routes
   - Verify response models
   - Test error cases (invalid nakshatra, etc.)

FRONTEND TESTS:
1. test_nakshatra_finder()
   - Render component
   - Select nakshatra
   - Mock API call
   - Verify results display

2. test_upcoming_dates()
   - Mock dashboard data
   - Verify all event types render
   - Check date formatting

Use pytest for backend, Jest for frontend.
```

---

# ðŸŽ¯ SUMMARY: WHAT YOU HAVE NOW

## Complete Package:

âœ… **Database Schema** - Ready to migrate  
âœ… **Backend Service** - Complete with caching  
âœ… **API Endpoints** - RESTful with validation  
âœ… **React Components** - Beautiful UI  
âœ… **Integration Guide** - With existing panchang  
âœ… **Step-by-Step Build Plan** - For beginners  
âœ… **Testing Strategy** - Comprehensive  
âœ… **Cursor AI Prompts** - Copy-paste ready

## Implementation Timeline:

- **Week 1:** Database + Backend (4-5 days)
- **Week 2:** API + Initial Data (4-5 days)
- **Week 3:** Frontend + Testing (4-5 days)

**Total: 3 weeks** (2-3 hours/day)

## Next Steps:

1. **Save this document** to your project
2. **Copy prompts** to Cursor AI one by one
3. **Follow step-by-step** guide
4. **Test thoroughly** before deploying
5. **Get pandit approval** before going live

---

**May this software serve temples and devotees well! ðŸ™**

**Hari Om ðŸ•‰ï¸**
