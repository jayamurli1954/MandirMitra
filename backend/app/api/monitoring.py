"""
System Monitoring API Endpoints
Provides health checks and system status for production monitoring
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any
import psutil
import os

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])


@router.get("/health")
def health_check():
    """
    Simple health check endpoint (no authentication required)
    Returns 200 if service is running
    """
    return {
        "status": "healthy",
        "service": "MandirMitra",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/status")
def get_system_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Comprehensive system status (admin only)
    Returns database, system resources, and application statistics
    """
    # Check admin permission
    if current_user.role not in ['admin', 'super_admin', 'temple_manager']:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access system status"
        )

    # Database check
    db_status = "unknown"
    db_error = None
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = "error"
        db_error = str(e)

    # System resources
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        system_resources = {
            "cpu_percent": round(cpu_percent, 2),
            "memory_percent": round(memory.percent, 2),
            "memory_available_mb": round(memory.available / (1024 * 1024), 2),
            "disk_percent": round(disk.percent, 2),
            "disk_free_gb": round(disk.free / (1024 * 1024 * 1024), 2)
        }
    except Exception as e:
        system_resources = {"error": str(e)}

    # Application statistics
    stats = {}
    try:
        from app.models.devotee import Devotee
        from app.models.donation import Donation
        from app.models.seva import SevaBooking
        from app.models.user import User as UserModel

        stats = {
            "total_devotees": db.query(Devotee).count(),
            "total_donations": db.query(Donation).count(),
            "total_seva_bookings": db.query(SevaBooking).count(),
            "total_users": db.query(UserModel).count(),
        }
    except Exception as e:
        stats = {"error": str(e)}

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "status": db_status,
            "error": db_error
        },
        "system": system_resources,
        "statistics": stats,
        "environment": {
            "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
            "deployment_mode": os.getenv("DEPLOYMENT_MODE", "unknown")
        }
    }


@router.get("/database/check")
def check_database_connection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Test database connectivity (admin only)
    """
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can check database"
        )

    try:
        # Simple query
        result = db.execute(text("SELECT version()"))
        version = result.fetchone()[0]

        # Count check
        from app.models.temple import Temple
        temple_count = db.query(Temple).count()

        return {
            "status": "connected",
            "database_version": version,
            "temple_count": temple_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )


@router.get("/resources")
def get_resource_usage(current_user: User = Depends(get_current_user)):
    """
    Get current system resource usage (admin only)
    Useful for monitoring CPU, memory, disk usage
    """
    if current_user.role not in ['admin', 'super_admin', 'temple_manager']:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can view resource usage"
        )

    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        # Memory
        memory = psutil.virtual_memory()

        # Disk
        disk = psutil.disk_usage('/')

        # Network (if available)
        try:
            network = psutil.net_io_counters()
            network_stats = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        except:
            network_stats = None

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "percent": round(cpu_percent, 2),
                "count": cpu_count,
                "status": "normal" if cpu_percent < 80 else "high"
            },
            "memory": {
                "total_mb": round(memory.total / (1024 * 1024), 2),
                "available_mb": round(memory.available / (1024 * 1024), 2),
                "used_mb": round(memory.used / (1024 * 1024), 2),
                "percent": round(memory.percent, 2),
                "status": "normal" if memory.percent < 85 else "high"
            },
            "disk": {
                "total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
                "free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
                "used_gb": round(disk.used / (1024 * 1024 * 1024), 2),
                "percent": round(disk.percent, 2),
                "status": "normal" if disk.percent < 90 else "low"
            },
            "network": network_stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get resource usage: {str(e)}"
        )
