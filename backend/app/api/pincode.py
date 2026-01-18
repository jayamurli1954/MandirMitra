"""
Pincode API - Auto-fill city and state from pincode
Uses local All_India_PINCode_master.csv file for fast lookups
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import csv
import os
from pathlib import Path

router = APIRouter()

# Cache the pincode data in memory for fast lookups
_pincode_cache = None

def load_pincode_data():
    """Load pincode data from CSV file and cache it"""
    global _pincode_cache
    
    if _pincode_cache is not None:
        return _pincode_cache
    
    # Find the CSV file in project root
    project_root = Path(__file__).parent.parent.parent.parent
    csv_file = project_root / "All_India_PINCode_master.csv"
    
    if not csv_file.exists():
        raise HTTPException(
            status_code=500,
            detail="Pincode data file not found. Please ensure All_India_PINCode_master.csv is in the project root."
        )
    
    try:
        # Create a lookup dictionary: pincode -> list of records
        # Multiple records can have the same pincode (different post offices)
        pincode_lookup = {}
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pincode = str(row.get('pincode', '')).strip()
                if pincode and pincode.isdigit() and len(pincode) == 6:
                    if pincode not in pincode_lookup:
                        pincode_lookup[pincode] = []
                    pincode_lookup[pincode].append(row)
        
        _pincode_cache = pincode_lookup
        return _pincode_cache
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading pincode data: {str(e)}"
        )


@router.get("/lookup")
def lookup_pincode(
    pincode: str = Query(..., description="6-digit pincode", min_length=6, max_length=6)
):
    """
    Lookup city and state from pincode using local JSON file.
    
    Returns the first matching record with:
    - district (city)
    - statename (state)
    - officename (post office name)
    """
    # Validate pincode format
    if not pincode.isdigit() or len(pincode) != 6:
        raise HTTPException(
            status_code=400,
            detail="Pincode must be a 6-digit number"
        )
    
    try:
        pincode_lookup = load_pincode_data()
        
        # Lookup pincode
        records = pincode_lookup.get(pincode, [])
        
        if not records:
            return {
                "pincode": pincode,
                "found": False,
                "message": "Pincode not found in database"
            }
        
        # Get first record (most common case)
        record = records[0]
        
        # Extract city and state
        # Use district as city, fallback to officename if district not available
        city = record.get('district', '').strip()
        if not city:
            city = record.get('officename', '').strip()
        
        state = record.get('statename', '').strip()
        
        # Format: Convert to title case (e.g., "WEST BENGAL" -> "West Bengal")
        def format_name(name):
            if not name:
                return name
            # Handle common cases
            parts = name.split()
            formatted = ' '.join([p.capitalize() for p in parts])
            return formatted
        
        return {
            "pincode": pincode,
            "found": True,
            "city": format_name(city),
            "state": format_name(state),
            "district": format_name(record.get('district', '')),
            "post_office": format_name(record.get('officename', '')),
            "total_matches": len(records)  # In case multiple post offices share same pincode
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error looking up pincode: {str(e)}"
        )


@router.get("/search")
def search_pincode(
    pincode: str = Query(..., description="Pincode to search (partial or full)", min_length=1, max_length=6)
):
    """
    Search for pincodes (supports partial matches for autocomplete).
    Returns list of matching pincodes with their city and state.
    """
    if not pincode.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Pincode must contain only digits"
        )
    
    try:
        pincode_lookup = load_pincode_data()
        
        # Find all pincodes that start with the given prefix
        matches = []
        for pin, records in pincode_lookup.items():
            if pin.startswith(pincode):
                if records:
                    record = records[0]
                    matches.append({
                        "pincode": pin,
                        "city": record.get('district', record.get('officename', '')),
                        "state": record.get('statename', '')
                    })
        
        # Sort by pincode
        matches.sort(key=lambda x: x['pincode'])
        
        # Limit to 20 results for performance
        return {
            "query": pincode,
            "matches": matches[:20],
            "total": len(matches)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching pincodes: {str(e)}"
        )

