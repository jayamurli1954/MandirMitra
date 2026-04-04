"""
Pincode API - Auto-fill city and state from pincode
Uses local All_India_PINCode_master.csv file for fast lookups and falls back to a live postal service.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, List
import csv
from pathlib import Path

import requests

router = APIRouter()

# Cache the pincode data in memory for fast lookups.
_pincode_cache: Optional[Dict[str, List[dict]]] = None
_remote_pincode_cache: Dict[str, dict] = {}


def _format_name(name: str) -> str:
    if not name:
        return name
    parts = str(name).strip().split()
    return " ".join([part.capitalize() for part in parts if part])


def load_pincode_data():
    """Load pincode data from CSV file and cache it."""
    global _pincode_cache

    if _pincode_cache is not None:
        return _pincode_cache

    project_root = Path(__file__).resolve().parents[3]
    candidate_files = [
        project_root / "data" / "All_India_PINCode_master.csv",
        project_root / "All_India_PINCode_master.csv",
        project_root / "backend" / "All_India_PINCode_master.csv",
    ]
    csv_file = next((path for path in candidate_files if path.exists()), None)

    if not csv_file:
        _pincode_cache = {}
        return _pincode_cache

    try:
        # Create a lookup dictionary: pincode -> list of records.
        # Multiple records can have the same pincode (different post offices).
        pincode_lookup = {}

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pincode = str(row.get("pincode", "")).strip()
                if pincode and pincode.isdigit() and len(pincode) == 6:
                    if pincode not in pincode_lookup:
                        pincode_lookup[pincode] = []
                    pincode_lookup[pincode].append(row)

        _pincode_cache = pincode_lookup
        return _pincode_cache

    except Exception:
        _pincode_cache = {}
        return _pincode_cache


def _lookup_remote_pincode(pincode: str) -> dict:
    """Fallback lookup using the public postal API."""
    cached = _remote_pincode_cache.get(pincode)
    if cached is not None:
        return cached

    try:
        response = requests.get(f"https://api.postalpincode.in/pincode/{pincode}", timeout=5)
        response.raise_for_status()
        payload = response.json()

        if isinstance(payload, list) and payload:
            item = payload[0] or {}
            post_offices = item.get("PostOffice") or []
            status = str(item.get("Status") or "").strip().lower()

            if status == "success" and post_offices:
                record = post_offices[0] or {}
                city = record.get("District") or record.get("Taluk") or record.get("Region") or record.get("Division") or record.get("Name")
                state = record.get("State") or ""
                result = {
                    "pincode": pincode,
                    "found": True,
                    "city": _format_name(city),
                    "state": _format_name(state),
                    "district": _format_name(record.get("District", "")),
                    "post_office": _format_name(record.get("Name", "")),
                    "total_matches": len(post_offices),
                    "source": "india_post",
                }
                _remote_pincode_cache[pincode] = result
                return result

        result = {
            "pincode": pincode,
            "found": False,
            "message": "Pincode not found in remote lookup",
            "source": "india_post",
        }
        _remote_pincode_cache[pincode] = result
        return result

    except Exception as exc:
        result = {
            "pincode": pincode,
            "found": False,
            "message": f"Remote pincode lookup failed: {str(exc)}",
            "source": "india_post",
        }
        _remote_pincode_cache[pincode] = result
        return result


@router.get("/lookup")
def lookup_pincode(
    pincode: str = Query(..., description="6-digit pincode", min_length=6, max_length=6)
):
    """
    Lookup city and state from pincode.

    Uses the local CSV first, then falls back to a remote postal lookup if needed.
    """
    if not pincode.isdigit() or len(pincode) != 6:
        raise HTTPException(status_code=400, detail="Pincode must be a 6-digit number")

    try:
        pincode_lookup = load_pincode_data()
        records = pincode_lookup.get(pincode, [])

        if records:
            record = records[0]
            city = record.get("district", "").strip() or record.get("officename", "").strip()
            state = record.get("statename", "").strip()

            return {
                "pincode": pincode,
                "found": True,
                "city": _format_name(city),
                "state": _format_name(state),
                "district": _format_name(record.get("district", "")),
                "post_office": _format_name(record.get("officename", "")),
                "total_matches": len(records),
                "source": "csv",
            }

        remote_result = _lookup_remote_pincode(pincode)
        if remote_result.get("found"):
            return remote_result

        return {
            "pincode": pincode,
            "found": False,
            "message": remote_result.get("message", "Pincode not found in database"),
            "source": remote_result.get("source", "remote"),
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error looking up pincode: {str(exc)}")


@router.get("/search")
def search_pincode(
    pincode: str = Query(..., description="Pincode to search (partial or full)", min_length=1, max_length=6)
):
    """
    Search for pincodes (supports partial matches for autocomplete).
    Returns list of matching pincodes with their city and state.
    """
    if not pincode.isdigit():
        raise HTTPException(status_code=400, detail="Pincode must contain only digits")

    try:
        pincode_lookup = load_pincode_data()

        matches = []
        for pin, records in pincode_lookup.items():
            if pin.startswith(pincode) and records:
                record = records[0]
                matches.append(
                    {
                        "pincode": pin,
                        "city": _format_name(record.get("district", record.get("officename", ""))),
                        "state": _format_name(record.get("statename", "")),
                    }
                )

        matches.sort(key=lambda x: x["pincode"])

        return {
            "query": pincode,
            "matches": matches[:20],
            "total": len(matches),
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error searching pincodes: {str(exc)}")
