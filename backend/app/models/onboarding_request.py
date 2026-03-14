"""Onboarding request model for public temple/trust registration."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class OnboardingRequest(Base):
    __tablename__ = "onboarding_requests"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(30), nullable=False, default="pending", index=True)

    temple_name = Column(String(200))
    temple_slug = Column(String(100))
    trust_name = Column(String(200))
    primary_deity = Column(String(100))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(20))
    phone = Column(String(20))
    email = Column(String(100))

    admin_full_name = Column(String(200), nullable=False)
    admin_email = Column(String(100), nullable=False, index=True)
    admin_phone = Column(String(20))

    review_notes = Column(Text)
    reviewed_at = Column(String)
    reviewed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    approved_temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True, index=True)
    approved_admin_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(
        String,
        default=lambda: datetime.utcnow().isoformat(),
        onupdate=lambda: datetime.utcnow().isoformat(),
    )

    reviewed_by = relationship("User", foreign_keys=[reviewed_by_user_id])
    approved_temple = relationship("Temple", foreign_keys=[approved_temple_id])
    approved_admin_user = relationship("User", foreign_keys=[approved_admin_user_id])
