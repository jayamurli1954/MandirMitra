"""
Sacred Events Cache Model
Stores pre-calculated important dates (Nakshatra, Ekadashi, Pradosha, etc.)
for quick lookup by counter clerks
"""

from sqlalchemy import Column, BigInteger, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from datetime import date, datetime

from app.core.database import Base


class SacredEventsCache(Base):
    """Cache table for sacred events dates"""
    
    __tablename__ = "sacred_events_cache"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    # Temple (for multi-tenant support)
    temple_id = Column(BigInteger, ForeignKey("temples.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Event Information
    event_code = Column(String(10), nullable=False, index=True)  # 'NAK', 'EK', 'SK', 'PR', 'PM', 'AM'
    event_name = Column(String(50), nullable=False)  # 'Rohini', 'Ekadashi', 'Sankashta Chaturthi', etc.
    
    # Date Information
    event_date = Column(Date, nullable=False, index=True)
    weekday = Column(String(10), nullable=True)  # 'Monday', 'Tuesday', etc.
    
    # Additional Information
    extra_info = Column(String(100), nullable=True)  # Optional additional details
    
    # Validity Period (for cache management)
    valid_from = Column(Date, nullable=True)
    valid_to = Column(Date, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())




















