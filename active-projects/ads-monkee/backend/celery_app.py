"""
Celery Application Configuration
=================================

Configures Celery for async task processing with Redis broker.
Per architecture: per-client concurrency=1, rate limits, idempotency.
"""

from celery import Celery
from backend.config import settings

# Initialize Celery app
celery_app = Celery(
    "ads_monkee",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["backend.tasks.analysis"]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Chicago",
    enable_utc=True,
    
    # Result backend settings
    result_expires=86400,  # 24 hours
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,  # One task at a time per worker
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (memory cleanup)
    
    # Task execution settings
    task_acks_late=True,  # Acknowledge after task completes
    task_reject_on_worker_lost=True,  # Reject if worker dies
    
    # Rate limiting (per architecture: per-client concurrency=1)
    task_default_rate_limit="10/m",  # Max 10 tasks per minute globally
    
    # Task routing
    task_routes={
        "backend.tasks.analysis.*": {"queue": "analysis"},
    },
    
    # Beat schedule (for future scheduled tasks)
    beat_schedule={
        # Will add weekly analysis schedule in v1.1
    },
)

# Task annotations for per-client concurrency control
celery_app.conf.task_annotations = {
    "*": {
        "rate_limit": "10/m",
        "time_limit": 3600,  # 1 hour hard limit
        "soft_time_limit": 3000,  # 50 minutes soft limit
    }
}

# ==============================================================================
# Health Check Task
# ==============================================================================

@celery_app.task(name="backend.tasks.health.smoke")
def smoke():
    """
    Smoke test task to verify Celery worker is functioning.
    
    Tests:
    - Redis connection (via Celery)
    - Database connection
    
    Returns:
        "ok" if all checks pass
    """
    from backend.database import get_sync_db
    from sqlalchemy import text
    
    # Test database connection
    with get_sync_db() as db:
        db.execute(text("SELECT 1"))
    
    return "ok"


if __name__ == "__main__":
    celery_app.start()

