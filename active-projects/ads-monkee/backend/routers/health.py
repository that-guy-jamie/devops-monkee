"""
Health Check Router
===================

Endpoints for monitoring system health.
"""

from fastapi import APIRouter, status
from sqlalchemy import text

from backend.config import settings
from backend.database import get_sync_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", status_code=status.HTTP_200_OK)
def health_check():
    """
    Health check endpoint.
    
    Checks:
    - Database connection
    - Redis connection (via Celery smoke task)
    
    Returns:
        {"status": "ok", "db": "ok", "redis": "ok", "celery": "ok"}
    """
    result = {
        "status": "ok",
        "db": "unknown",
        "redis": "unknown",
        "celery": "unknown",
    }
    
    # Check database
    try:
        with get_sync_db() as db:
            db.execute(text("SELECT 1"))
        result["db"] = "ok"
    except Exception as e:
        result["db"] = f"error: {str(e)}"
        result["status"] = "degraded"
    
    # Check Redis/Celery
    try:
        from backend.celery_app import celery_app, smoke
        
        # Try to get Celery stats (checks Redis connection)
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            result["redis"] = "ok"
            result["celery"] = "ok"
        else:
            result["redis"] = "no workers"
            result["celery"] = "no workers"
            result["status"] = "degraded"
    except Exception as e:
        result["redis"] = f"error: {str(e)}"
        result["celery"] = f"error: {str(e)}"
        result["status"] = "degraded"
    
    return result

