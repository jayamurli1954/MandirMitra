# 📅 TODAY'S PANCHANG DISPLAY - COMPLETE GUIDE
## What to Show, How to Show It, and Why

**For:** Temple Management Software UI/UX  
**Target Users:** Devotees, Temple Staff, Pandits  
**Context:** Indian Hindu Temples  
**Last Updated:** November 2024

---

# TABLE OF CONTENTS

1. [Essential Elements - Must Have](#section-1)
2. [Secondary Elements - Should Have](#section-2)
3. [Advanced Elements - Nice to Have](#section-3)
4. [UI/UX Design Examples](#section-4)
5. [Multi-Language Display](#section-5)
6. [Responsive Design Considerations](#section-6)
7. [Print Format](#section-7)
8. [API Response Format](#section-8)

---

<a name="section-1"></a>
# 1. ESSENTIAL ELEMENTS - MUST HAVE

## 1.1 Date Information

### Gregorian Date
```
Display: Saturday, November 23, 2024
Format: DayName, MonthName DD, YYYY
Why: Users need to correlate with modern calendar
```

### Hindu Calendar Date
```
Display: 
- Vikram Samvat: 2081
- Shaka Samvat: 1946
- Month: Kartik (कार्तिक)
- Paksha: Krishna Paksha (कृष्ण पक्ष)

Why: Religious context, festival identification
```

### Day of Week (Vara)
```
Display: 
- English: Saturday
- Hindi: शनिवार (Shanivar)
- Sanskrit: शनिवासरः (Shanivasara)
- Ruling Planet: Saturn (Shani)
- Associated Deity: Lord Shani, Hanuman

Why: Many devotees observe specific day-based fasts/rituals
```

## 1.2 The Five Limbs (Panch-Anga)

### 1. Tithi (तिथि)

**Display Format:**
```
╔════════════════════════════════════════╗
║  TITHI                                 ║
╠════════════════════════════════════════╣
║  Krishna Dwadashi (कृष्ण द्वादशी)      ║
║  Until: 2:45 PM                        ║
║  Then: Krishna Trayodashi              ║
╚════════════════════════════════════════╝
```

**Information to Show:**
- Current tithi name (English + Sanskrit/Hindi)
- Paksha (Shukla/Krishna)
- End time (when it transitions)
- Next tithi name
- Special significance if any

**Special Tithi Indicators:**
```
🌕 PURNIMA (Full Moon)
🌑 AMAVASYA (New Moon)
⭐ EKADASHI (Fasting Day)
🙏 PRADOSH (Trayodashi - Shiva worship)
```

**Why Critical:**
- Determines fasting days (Ekadashi)
- Festival dates
- Auspiciousness for activities

### 2. Nakshatra (नक्षत्र)

**Display Format:**
```
╔════════════════════════════════════════╗
║  NAKSHATRA                             ║
╠════════════════════════════════════════╣
║  Rohini (रोहिणी)                       ║
║  Pada: 2 (चरण: २)                      ║
║  Until: 11:30 AM                       ║
║  Deity: Brahma (ब्रह्मा)                ║
║  Nature: ⭐ Very Auspicious            ║
╚════════════════════════════════════════╝
```

**Information to Show:**
- Nakshatra name (English + Sanskrit/Hindi)
- Current Pada (quarter 1-4)
- End time
- Associated deity
- Nature/Quality (Auspicious/Inauspicious/Mixed)
- Ruling planet

**Quality Indicators:**
```
⭐⭐⭐ Pushya, Rohini - MOST Auspicious
⭐⭐ Hasta, Swati - Very Auspicious  
⭐ Anuradha, Mrigashira - Auspicious
⚠️ Mula, Ardra, Ashlesha - Inauspicious
```

**Why Critical:**
- Birth nakshatra for naming ceremonies
- Muhurat selection for sevas
- Marriage compatibility

### 3. Yoga (योग)

**Display Format:**
```
╔════════════════════════════════════════╗
║  YOGA                                  ║
╠════════════════════════════════════════╣
║  Siddhi (सिद्धि)                       ║
║  Nature: ✅ Auspicious                 ║
║  Until: 4:20 PM                        ║
╚════════════════════════════════════════╝
```

**Information to Show:**
- Yoga name (English + Sanskrit/Hindi)
- Nature (Auspicious/Inauspicious)
- End time
- Special note for bad yogas

**Critical Warnings:**
```
⚠️ VYATIPATA - AVOID ALL ACTIVITIES
⚠️ VAIDHRITI - AVOID ALL ACTIVITIES
```

**Why Important:**
- Vyatipata & Vaidhriti are extremely inauspicious
- Can override otherwise good muhurat

### 4. Karana (करण)

**Display Format:**
```
╔════════════════════════════════════════╗
║  KARANA                                ║
╠════════════════════════════════════════╣
║  First Half: Bava (बव)                ║
║  Until: 8:15 AM                        ║
║                                        ║
║  Second Half: Balava (बालव)           ║
║  Until: 6:30 PM                        ║
╚════════════════════════════════════════╝
```

**Information to Show:**
- Current karana name
- End time
- Note if Vishti/Bhadra (inauspicious)

**Critical Warning:**
```
⚠️ BHADRA (Vishti) - Avoid starting new activities
```

**Why Important:**
- Bhadra karana is highly inauspicious
- Occurs 8 times per month
- Many devotees specifically avoid it

### 5. Additional Core Info

**Month (Maasa)**
```
Hindu Month: Kartik (कार्तिक)
Season: Sharad (शरद् - Autumn)
```

## 1.3 Sun Timings

**Display Format:**
```
╔════════════════════════════════════════╗
║  SUN TIMINGS                           ║
╠════════════════════════════════════════╣
║  🌅 Sunrise:    6:15 AM               ║
║  🌇 Sunset:     5:45 PM               ║
║  Day Duration:  11h 30m               ║
╚════════════════════════════════════════╝
```

**Why Critical:**
- Religious activities tied to sunrise
- Tithi at sunrise determines the day
- Sandhya (twilight) worship timings

## 1.4 Inauspicious Times (CRITICAL!)

### Rahu Kaal (राहु काल)

**Display Format:**
```
╔════════════════════════════════════════╗
║  ⚠️ RAHU KAAL (INAUSPICIOUS)          ║
╠════════════════════════════════════════╣
║  10:30 AM - 12:00 PM                  ║
║  Duration: 1 hour 30 minutes          ║
║                                        ║
║  ❌ AVOID:                             ║
║  • Starting new work                   ║
║  • Important meetings                  ║
║  • Travel (especially to north)        ║
║  • Financial transactions              ║
╚════════════════════════════════════════╝
```

**Must Include:**
- Start time (precise to minute)
- End time
- Duration
- What to avoid (in simple language)

### Yamaganda (यमगण्ड)

**Display Format:**
```
╔════════════════════════════════════════╗
║  ⚠️ YAMAGANDA (INAUSPICIOUS)          ║
╠════════════════════════════════════════╣
║  3:00 PM - 4:30 PM                    ║
║  Duration: 1 hour 30 minutes          ║
╚════════════════════════════════════════╝
```

### Gulika (गुलिक)

**Display Format:**
```
╔════════════════════════════════════════╗
║  ⚠️ GULIKA (INAUSPICIOUS)             ║
╠════════════════════════════════════════╣
║  7:45 AM - 9:15 AM                    ║
║  Duration: 1 hour 30 minutes          ║
╚════════════════════════════════════════╝
```

**Why EXTREMELY Important:**
- Most devotees actively avoid these times
- Will call temple to check timings
- Affects seva booking drastically
- Missing this = angry devotees!

## 1.5 Auspicious Times

### Abhijit Muhurat (अभिजित मुहूर्त)

**Display Format:**
```
╔════════════════════════════════════════╗
║  ✅ ABHIJIT MUHURAT (MOST AUSPICIOUS) ║
╠════════════════════════════════════════╣
║  11:45 AM - 12:35 PM                  ║
║  Duration: 50 minutes                  ║
║                                        ║
║  ✅ BEST FOR:                          ║
║  • All auspicious activities           ║
║  • Overrides other doshas              ║
║  • "Golden time" of the day            ║
╚════════════════════════════════════════╝
```

**Why Important:**
- Considered supremely auspicious
- Can nullify other bad timings
- Very popular for important activities

### Brahma Muhurat (ब्रह्म मुहूर्त)

**Display Format:**
```
╔════════════════════════════════════════╗
║  🌄 BRAHMA MUHURAT (Spiritual)        ║
╠════════════════════════════════════════╣
║  4:39 AM - 6:15 AM                    ║
║  (96 minutes before sunrise)           ║
║                                        ║
║  Best for: Meditation, Yoga, Study     ║
╚════════════════════════════════════════╝
```

---

<a name="section-2"></a>
# 2. SECONDARY ELEMENTS - SHOULD HAVE

## 2.1 Festivals & Special Days

**Display Format:**
```
╔════════════════════════════════════════╗
║  🎉 TODAY'S SIGNIFICANCE               ║
╠════════════════════════════════════════╣
║  • Kartik Purnima (कार्तिक पूर्णिमा)   ║
║  • Dev Deepawali (देव दीपावली)        ║
║  • Ganga Snan (गंगा स्नान) - Holy Bath║
║                                        ║
║  Special Observances:                  ║
║  • Light diyas at Ganga ghats          ║
║  • Tulsi vivah in some regions         ║
╚════════════════════════════════════════╝
```

**Show if applicable:**
- Festival name (multiple if coinciding)
- Regional variations
- Special rituals
- Significance

## 2.2 Recommended Activities

**Display Format:**
```
╔════════════════════════════════════════╗
║  ✅ GOOD FOR TODAY                     ║
╠════════════════════════════════════════╣
║  • Spiritual practices                 ║
║  • Charity & donations                 ║
║  • Starting education                  ║
║  • Property purchase                   ║
╚════════════════════════════════════════╝
```

```
╔════════════════════════════════════════╗
║  ❌ AVOID TODAY                        ║
╠════════════════════════════════════════╣
║  • Marriage ceremonies                 ║
║  • Starting construction                ║
║  • Travel to south direction           ║
╚════════════════════════════════════════╝
```

## 2.3 Fasting Information

**Display Format:**
```
╔════════════════════════════════════════╗
║  🍃 FASTING (उपवास)                   ║
╠════════════════════════════════════════╣
║  Type: Shanivar Vrat (शनिवार व्रत)    ║
║                                        ║
║  Observances:                          ║
║  • Visit Hanuman temple                ║
║  • Offer mustard oil to Shani          ║
║  • Wear black/blue clothes             ║
║  • Chant Hanuman Chalisa               ║
║                                        ║
║  Food: Fruits and milk allowed         ║
║  Break Fast After: Sunset (5:45 PM)    ║
╚════════════════════════════════════════╝
```

**Show for:**
- Ekadashi (no grains)
- Pradosh (evening fast)
- Shivaratri (complete fast)
- Day-specific fasts (Monday, Tuesday, etc.)

## 2.4 Planetary Positions (Optional but Valuable)

**Display Format:**
```
╔════════════════════════════════════════╗
║  PLANETARY POSITIONS (ग्रह स्थिति)     ║
╠════════════════════════════════════════╣
║  Sun (सूर्य):      Scorpio (वृश्चिक)   ║
║  Moon (चन्द्र):    Taurus (वृषभ)       ║
║  Mars (मंगल):     Cancer (कर्क)       ║
║  Mercury (बुध):    Scorpio (वृश्चिक)   ║
║  Jupiter (गुरु):   Aries (मेष)         ║
║  Venus (शुक्र):    Libra (तुला)        ║
║  Saturn (शनि):     Aquarius (कुम्भ)    ║
╚════════════════════════════════════════╝
```

## 2.5 Panchak Period Warning

**If applicable:**
```
╔════════════════════════════════════════╗
║  ⚠️ PANCHAK PERIOD ACTIVE              ║
╠════════════════════════════════════════╣
║  From: Nov 20, 3:00 PM                ║
║  To:   Nov 23, 8:00 PM                ║
║                                        ║
║  AVOID:                                ║
║  • Cremation (unless with remedies)    ║
║  • House construction (roof)           ║
║  • Travel to south direction           ║
║                                        ║
║  Remedies available - consult pandit   ║
╚════════════════════════════════════════╝
```

**Why Important:**
- Panchak is 5 nakshatras considered inauspicious
- Serious religious implications
- Remedies are complex

---

<a name="section-3"></a>
# 3. ADVANCED ELEMENTS - NICE TO HAVE

## 3.1 Choghadiya (चौघड़िया)

**For Business/Travel Muhurat:**

```
╔════════════════════════════════════════╗
║  CHOGHADIYA MUHURAT                    ║
╠════════════════════════════════════════╣
║  DAY CHOGHADIYA (6:15 AM - 5:45 PM)   ║
║                                        ║
║  6:15 - 7:55 AM   Udveg    ⚠️         ║
║  7:55 - 9:35 AM   Char     ✅ Good    ║
║  9:35 - 11:15 AM  Labh     ✅ Best    ║
║  11:15 AM - 12:55 PM Amrit ✅ Best    ║
║  12:55 - 2:35 PM  Kaal     ❌ Bad     ║
║  2:35 - 4:15 PM   Shubh    ✅ Good    ║
║  4:15 - 5:45 PM   Rog      ⚠️         ║
║                                        ║
║  NIGHT CHOGHADIYA (5:45 PM - 6:15 AM) ║
║  5:45 - 7:25 PM   Kaal     ❌ Bad     ║
║  [... continues ...]                   ║
╚════════════════════════════════════════╝
```

## 3.2 Hora (होरा) - Planetary Hours

```
╔════════════════════════════════════════╗
║  HORA (Planetary Hours)                ║
╠════════════════════════════════════════╣
║  Current: Saturn Hora (शनि होरा)      ║
║  From: 10:30 AM                        ║
║  Until: 11:25 AM                       ║
║  Nature: Not favorable for new starts  ║
║                                        ║
║  Next: Jupiter Hora (गुरु होरा) ✅    ║
║  Starts: 11:25 AM                      ║
║  Good for: Education, legal matters    ║
╚════════════════════════════════════════╝
```

## 3.3 Nakshatra-Wise Muhurat

```
╔════════════════════════════════════════╗
║  SPECIAL MUHURAT FOR TODAY             ║
╠════════════════════════════════════════╣
║  For Marriage: Not Suitable            ║
║  Reason: Rohini is good, but Krishna   ║
║  Paksha not ideal for marriage         ║
║                                        ║
║  For Griha Pravesh: ✅ Excellent       ║
║  Time: 11:45 AM - 12:35 PM (Abhijit)  ║
║                                        ║
║  For Business Start: ✅ Good           ║
║  Time: Morning after 9:15 AM           ║
╚════════════════════════════════════════╝
```

## 3.4 Name Letter (for babies born today)

```
╔════════════════════════════════════════╗
║  👶 FOR BABIES BORN TODAY              ║
╠════════════════════════════════════════╣
║  Nakshatra: Rohini, Pada 2            ║
║  Name should start with: Va (वा)       ║
║                                        ║
║  Suggestions:                          ║
║  Boys: Varun, Vamsi, Vatsal           ║
║  Girls: Vanita, Varsha, Vani          ║
╚════════════════════════════════════════╝
```

## 3.5 Zodiac Sign Transit

```
╔════════════════════════════════════════╗
║  IMPORTANT TRANSITS                    ║
╠════════════════════════════════════════╣
║  🌙 Moon in: Taurus (वृषभ)            ║
║  Good for: Material comforts           ║
║                                        ║
║  ⚠️ Upcoming: Saturn transit to Pisces║
║  Date: March 2025                      ║
║  Impact: Major life changes            ║
╚════════════════════════════════════════╝
```

---

<a name="section-4"></a>
# 4. UI/UX DESIGN EXAMPLES

## 4.1 Dashboard Widget (Compact View)

**For Temple Management Dashboard:**

```
┌─────────────────────────────────────────┐
│  📅 TODAY'S PANCHANG                    │
│  Saturday, November 23, 2024            │
├─────────────────────────────────────────┤
│                                         │
│  Tithi: Krishna Dwadashi → 2:45 PM     │
│  Nakshatra: Rohini ⭐ → 11:30 AM       │
│  Yoga: Siddhi ✅                       │
│                                         │
│  🌅 6:15 AM  🌇 5:45 PM                │
│                                         │
│  ⚠️ AVOID:                              │
│  • Rahu Kaal: 10:30 AM - 12:00 PM      │
│                                         │
│  ✅ BEST TIME:                          │
│  • Abhijit: 11:45 AM - 12:35 PM        │
│                                         │
│  [View Full Panchang]                   │
└─────────────────────────────────────────┘
```

## 4.2 Full Page View (Detailed)

**For Devotee-Facing Website/App:**

```
╔═══════════════════════════════════════════════════════════╗
║                    🕉️ TODAY'S PANCHANG                    ║
║           Saturday, November 23, 2024                     ║
║     Vikram Samvat 2081 | Kartik Krishna Dwadashi         ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │  THE FIVE LIMBS (Panch-Anga)                        │ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │  1. TITHI (तिथि)                                    │ ║
║  │     Krishna Dwadashi (कृष्ण द्वादशी)                 │ ║
║  │     Until 2:45 PM, Then Krishna Trayodashi          │ ║
║  │                                                      │ ║
║  │  2. NAKSHATRA (नक्षत्र)                             │ ║
║  │     Rohini (रोहिणी) ⭐⭐ Very Auspicious            │ ║
║  │     Pada: 2, Deity: Brahma                          │ ║
║  │     Until 11:30 AM, Then Mrigashira                 │ ║
║  │                                                      │ ║
║  │  3. YOGA (योग)                                       │ ║
║  │     Siddhi (सिद्धि) ✅ Auspicious                   │ ║
║  │     Until 4:20 PM                                    │ ║
║  │                                                      │ ║
║  │  4. KARANA (करण)                                     │ ║
║  │     First Half: Bava (until 8:15 AM)                │ ║
║  │     Second Half: Balava (until 6:30 PM)             │ ║
║  │                                                      │ ║
║  │  5. VARA (वार)                                       │ ║
║  │     Shanivar (शनिवार) - Saturday                    │ ║
║  │     Deity: Lord Shani, Hanuman                      │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │  SUN & MOON                                          │ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │  🌅 Sunrise: 6:15 AM                                │ ║
║  │  🌇 Sunset:  5:45 PM                                │ ║
║  │  🌄 Brahma Muhurat: 4:39 AM - 6:15 AM               │ ║
║  │  🌙 Moonrise: 10:45 PM                              │ ║
║  │  🌙 Moonset: 11:30 AM                               │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │  ⚠️ INAUSPICIOUS TIMES - AVOID                      │ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │  Rahu Kaal:  10:30 AM - 12:00 PM (1h 30m)          │ ║
║  │  Yamaganda:  3:00 PM - 4:30 PM (1h 30m)            │ ║
║  │  Gulika:     7:45 AM - 9:15 AM (1h 30m)            │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │  ✅ AUSPICIOUS TIMES - BEST FOR ACTIVITIES          │ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │  Abhijit Muhurat: 11:45 AM - 12:35 PM (50m)        │ ║
║  │  → Most auspicious time of the day                  │ ║
║  │  → Good for all activities                          │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │  🎉 SPECIAL OBSERVANCES                             │ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │  • Saturday (Shanivar) - Visit Hanuman Temple       │ ║
║  │  • Offer mustard oil to Lord Shani                  │ ║
║  │  • Chant Hanuman Chalisa                            │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │  📖 DID YOU KNOW?                                    │ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │  Rohini nakshatra is considered one of the most     │ ║
║  │  auspicious nakshatras. It's ruled by Brahma and    │ ║
║  │  is excellent for material growth and prosperity.   │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║           [Download PDF] [Share] [Set Reminder]          ║
╚═══════════════════════════════════════════════════════════╝
```

## 4.3 Mobile App View (Compact)

**For Temple Mobile App:**

```
┌───────────────────────┐
│ 📅 Today's Panchang   │
├───────────────────────┤
│                       │
│ Sat, Nov 23, 2024    │
│ Kartik K. Dwadashi   │
│                       │
│ ━━━━━━━━━━━━━━━━━━━  │
│                       │
│ 📆 TITHI              │
│ Krishna Dwadashi      │
│ Until 2:45 PM         │
│                       │
│ ⭐ NAKSHATRA          │
│ Rohini ⭐⭐          │
│ Until 11:30 AM        │
│                       │
│ 🌅 SUN                │
│ ↑ 6:15 AM ↓ 5:45 PM  │
│                       │
│ ━━━━━━━━━━━━━━━━━━━  │
│                       │
│ ⚠️ AVOID              │
│ Rahu: 10:30-12:00    │
│                       │
│ ✅ BEST TIME          │
│ Abhijit: 11:45-12:35 │
│                       │
│ [View Details]        │
│                       │
└───────────────────────┘
```

## 4.4 Print Format (A4)

**For Temple Office/Counter:**

```
════════════════════════════════════════════════════════════
                    SHRI [TEMPLE NAME]
                    [Temple Address]
                    
              🕉️ TODAY'S PANCHANG (आज का पंचांग) 🕉️
════════════════════════════════════════════════════════════

DATE: Saturday, November 23, 2024
HINDU DATE: Vikram Samvat 2081, Kartik Krishna Dwadashi

────────────────────────────────────────────────────────────
PANCH-ANGA (Five Limbs)
────────────────────────────────────────────────────────────

1. TITHI (तिथि): Krishna Dwadashi (कृष्ण द्वादशी)
   Until: 2:45 PM
   Next: Krishna Trayodashi

2. NAKSHATRA (नक्षत्र): Rohini (रोहिणी) ⭐ Very Auspicious
   Pada: 2
   Deity: Brahma
   Until: 11:30 AM

3. YOGA (योग): Siddhi (सिद्धि) - Auspicious
   Until: 4:20 PM

4. KARANA (करण): Bava (until 8:15 AM), Balava (until 6:30 PM)

5. VARA (वार): Shanivar (शनिवार) - Saturday
   Ruling Planet: Saturn (Shani)
   Associated Deities: Lord Shani, Hanuman

────────────────────────────────────────────────────────────
SUN & MOON TIMINGS
────────────────────────────────────────────────────────────

Sunrise (सूर्योदय):        6:15 AM
Sunset (सूर्यास्त):         5:45 PM
Moonrise (चन्द्रोदय):      10:45 PM
Moonset (चन्द्रास्त):       11:30 AM

Brahma Muhurat:           4:39 AM - 6:15 AM

────────────────────────────────────────────────────────────
⚠️ INAUSPICIOUS TIMES (अशुभ काल) - AVOID THESE
────────────────────────────────────────────────────────────

Rahu Kaal (राहु काल):     10:30 AM - 12:00 PM (1h 30m)
Yamaganda (यमगण्ड):       3:00 PM - 4:30 PM (1h 30m)
Gulika (गुलिक):           7:45 AM - 9:15 AM (1h 30m)

AVOID: Starting new work, important meetings, travel (north),
       financial transactions, medical procedures

────────────────────────────────────────────────────────────
✅ AUSPICIOUS TIMES (शुभ मुहूर्त)
────────────────────────────────────────────────────────────

Abhijit Muhurat:          11:45 AM - 12:35 PM (50 minutes)
                          → BEST TIME for all activities

────────────────────────────────────────────────────────────
SPECIAL OBSERVANCES
────────────────────────────────────────────────────────────

Today is Saturday (Shanivar):
• Visit Hanuman Temple
• Offer mustard oil to Lord Shani
• Wear black or blue clothes
• Chant Hanuman Chalisa
• Many observe fast today

────────────────────────────────────────────────────────────
RECOMMENDED ACTIVITIES FOR TODAY
────────────────────────────────────────────────────────────

✅ GOOD FOR:
   • Spiritual practices and meditation
   • Charity and donations (दान)
   • Property purchase
   • Starting education

❌ AVOID:
   • Marriage ceremonies
   • Starting major construction
   • Activities during Rahu Kaal (see above)

────────────────────────────────────────────────────────────

For Seva Bookings: Visit temple office or call [Phone]
Next Ekadashi: [Date]
Next Purnima: [Date]

════════════════════════════════════════════════════════════
Generated by MandirSync Temple Management Software
Verified against Rashtriya Panchang | Accurate to IST
════════════════════════════════════════════════════════════
```

---

<a name="section-5"></a>
# 5. MULTI-LANGUAGE DISPLAY

## 5.1 Language Options

**Must Support:**
- English (default)
- Hindi (हिंदी)
- Sanskrit (संस्कृत)

**Should Support (based on region):**
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Kannada (ಕನ್ನಡ)
- Marathi (मराठी)
- Bengali (বাংলা)
- Gujarati (ગુજરાતી)

## 5.2 Example - Hindi Display

```
╔════════════════════════════════════════╗
║         आज का पंचांग                   ║
║    शनिवार, २३ नवंबर, २०२४              ║
╠════════════════════════════════════════╣
║                                        ║
║  तिथि: कृष्ण द्वादशी                   ║
║  समाप्ति: दोपहर २:४५ बजे              ║
║                                        ║
║  नक्षत्र: रोहिणी ⭐⭐                  ║
║  पाद: २                                ║
║  समाप्ति: सुबह ११:३० बजे              ║
║                                        ║
║  योग: सिद्धि ✅                        ║
║  करण: बव (प्रथम), बालव (द्वितीय)      ║
║                                        ║
║  🌅 सूर्योदय: ६:१५ पूर्वाह्न          ║
║  🌇 सूर्यास्त: ५:४५ अपराह्न           ║
║                                        ║
║  ⚠️ अशुभ काल:                         ║
║  राहु काल: १०:३० - १२:०० बजे         ║
║                                        ║
║  ✅ शुभ मुहूर्त:                       ║
║  अभिजित: ११:४५ - १२:३५ बजे           ║
╚════════════════════════════════════════╝
```

---

<a name="section-6"></a>
# 6. COLOR CODING & VISUAL INDICATORS

## 6.1 Color Scheme

**Auspicious Elements:**
```
Color: Green (#28A745) or Gold (#FFD700)
Icon: ✅ ⭐ 🌟
Examples: Good nakshatras, Abhijit muhurat
```

**Inauspicious Elements:**
```
Color: Red (#DC3545) or Orange (#FF6B6B)
Icon: ⚠️ ❌ ⛔
Examples: Rahu Kaal, Bhadra, bad yogas
```

**Neutral/Info:**
```
Color: Blue (#007BFF) or Gray (#6C757D)
Icon: ℹ️ 📋 📅
Examples: General info, timestamps
```

**Special/Festival:**
```
Color: Purple (#6F42C1) or Saffron (#FF9933)
Icon: 🎉 🙏 🕉️
Examples: Festivals, special observances
```

---

<a name="section-7"></a>
# 7. KEY DISPLAY PRINCIPLES

## 7.1 Information Hierarchy

**Priority 1 (Always Visible):**
1. Date (both Gregorian and Hindu)
2. Tithi with end time
3. Nakshatra with quality indicator
4. Rahu Kaal timing
5. Sunrise/Sunset

**Priority 2 (Prominently Displayed):**
1. Yoga
2. Karana
3. Abhijit Muhurat
4. Yamaganda & Gulika
5. Special observances/festivals

**Priority 3 (Secondary/Expandable):**
1. Choghadiya
2. Hora
3. Planetary positions
4. Panchak warning
5. Recommended activities

## 7.2 User Experience Guidelines

**DO:**
- ✅ Use large, readable fonts (min 14px for body)
- ✅ Color-code auspicious vs inauspicious
- ✅ Show times in 12-hour format with AM/PM
- ✅ Provide both English and local language
- ✅ Make Rahu Kaal VERY prominent (users ask most)
- ✅ Show "until XX:XX" for changing elements
- ✅ Use icons for quick visual scanning
- ✅ Provide "Share" and "Download" options
- ✅ Update automatically at transition times

**DON'T:**
- ❌ Clutter with too much info on one screen
- ❌ Use only 24-hour time format
- ❌ Hide inauspicious times (users NEED to know)
- ❌ Use technical jargon without explanation
- ❌ Show outdated info (cache properly)
- ❌ Forget mobile responsiveness
- ❌ Omit end times for tithis/nakshatras

---

<a name="section-8"></a>
# 8. API RESPONSE FORMAT

## Sample JSON Structure

```json
{
  "date": {
    "gregorian": {
      "date": "2024-11-23",
      "day": "Saturday",
      "formatted": "Saturday, November 23, 2024"
    },
    "hindu": {
      "samvat_vikram": 2081,
      "samvat_shaka": 1946,
      "month": "Kartik",
      "month_sanskrit": "कार्तिक",
      "paksha": "Krishna",
      "paksha_sanskrit": "कृष्ण पक्ष"
    }
  },
  
  "panchang": {
    "tithi": {
      "number": 12,
      "name": "Dwadashi",
      "sanskrit": "द्वादशी",
      "paksha": "Krishna",
      "full_name": "Krishna Dwadashi",
      "end_time": "2024-11-23T14:45:00+05:30",
      "next_tithi": "Krishna Trayodashi",
      "is_special": false,
      "special_type": null
    },
    
    "nakshatra": {
      "number": 4,
      "name": "Rohini",
      "sanskrit": "रोहिणी",
      "deity": "Brahma",
      "ruling_planet": "Moon",
      "pada": 2,
      "end_time": "2024-11-23T11:30:00+05:30",
      "next_nakshatra": "Mrigashira",
      "quality": "very_auspicious",
      "quality_stars": 3,
      "moon_longitude": 45.67
    },
    
    "yoga": {
      "number": 16,
      "name": "Siddhi",
      "sanskrit": "सिद्धि",
      "nature": "auspicious",
      "end_time": "2024-11-23T16:20:00+05:30",
      "is_bad_yoga": false
    },
    
    "karana": {
      "first_half": {
        "name": "Bava",
        "end_time": "2024-11-23T08:15:00+05:30"
      },
      "second_half": {
        "name": "Balava",
        "end_time": "2024-11-23T18:30:00+05:30"
      },
      "is_bhadra": false
    },
    
    "vara": {
      "number": 6,
      "name": "Saturday",
      "sanskrit": "शनिवार",
      "ruling_planet": "Saturn",
      "deity": "Shani, Hanuman"
    }
  },
  
  "sun_moon": {
    "sunrise": "2024-11-23T06:15:00+05:30",
    "sunset": "2024-11-23T17:45:00+05:30",
    "moonrise": "2024-11-23T22:45:00+05:30",
    "moonset": "2024-11-23T11:30:00+05:30",
    "day_duration_hours": 11.5
  },
  
  "inauspicious_times": {
    "rahu_kaal": {
      "start": "2024-11-23T10:30:00+05:30",
      "end": "2024-11-23T12:00:00+05:30",
      "duration_minutes": 90
    },
    "yamaganda": {
      "start": "2024-11-23T15:00:00+05:30",
      "end": "2024-11-23T16:30:00+05:30",
      "duration_minutes": 90
    },
    "gulika": {
      "start": "2024-11-23T07:45:00+05:30",
      "end": "2024-11-23T09:15:00+05:30",
      "duration_minutes": 90
    }
  },
  
  "auspicious_times": {
    "abhijit_muhurat": {
      "start": "2024-11-23T11:45:00+05:30",
      "end": "2024-11-23T12:35:00+05:30",
      "duration_minutes": 50
    },
    "brahma_muhurat": {
      "start": "2024-11-23T04:39:00+05:30",
      "end": "2024-11-23T06:15:00+05:30",
      "duration_minutes": 96
    }
  },
  
  "festivals": [
    {
      "name": "Shani Pradosh Vrat",
      "regional": false,
      "type": "fasting",
      "description": "Saturday Pradosh - Shiva worship in evening"
    }
  ],
  
  "recommendations": {
    "good_for": [
      "Spiritual practices",
      "Charity and donations",
      "Property purchase"
    ],
    "avoid": [
      "Marriage ceremonies",
      "Starting construction",
      "Travel during Rahu Kaal"
    ]
  },
  
  "location": {
    "city": "Bangalore",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "timezone": "Asia/Kolkata"
  },
  
  "calculation_metadata": {
    "ayanamsa_type": "LAHIRI",
    "ayanamsa_value": 24.1567,
    "generated_at": "2024-11-23T00:00:00+05:30",
    "verified_against": "drikpanchang.com"
  }
}
```

---

# SUMMARY: MINIMUM VIABLE PANCHANG DISPLAY

**For a basic temple software, MUST show:**

1. ✅ Date (Gregorian + Hindu)
2. ✅ Tithi with end time
3. ✅ Nakshatra with quality
4. ✅ Sunrise & Sunset
5. ✅ Rahu Kaal (with WARNING)
6. ✅ Abhijit Muhurat
7. ✅ Day-specific observances
8. ✅ Festivals (if any)

**Total screen space:** Can fit in 1/3 of dashboard

**Update frequency:** 
- Check every minute for transitions
- Highlight when tithi/nakshatra changing soon

**Key principle:** 
**CLARITY > COMPLETENESS**  
Better to show 8 things clearly than 20 things confusingly!

---

**END OF GUIDE**
