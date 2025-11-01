"""
Report generation API endpoints.

Handles triggering report generation via Celery job queue.
"""

from fastapi import APIRouter, HTTPException
import logging

from api.models.requests import GenerateReportRequest
from api.models.responses import JobResponse
from api.config import settings
from worker.tasks import execute_report_generation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/generate", response_model=JobResponse)
async def generate_report(request: GenerateReportRequest):
    """
    Generate a Markdown report as a background job.
    
    This endpoint queues report generation and immediately returns a job ID.
    The report generation runs asynchronously in the background worker.
    
    Args:
        request: Report generation request with slug and scope
    
    Returns:
        JobResponse with job_id and initial status
    
    Raises:
        HTTPException: If Redis connection fails or job creation fails
    
    Example:
        POST /api/reports/generate
        {
            "slug": "priority-roofing",
            "scope": "LAST-30-DAYS"
        }
        
        Response:
        {
            "job_id": "xyz789-uvw456",
            "status": "queued"
        }
    """
    logger.info(f"Received report generation request: {request.slug} scope={request.scope}")
    
    try:
        # Enqueue the report generation using Celery
        task = execute_report_generation.apply_async(
            kwargs={
                'slug': request.slug,
                'scope': request.scope
            }
        )
        
        logger.info(f"Report task created: {task.id} for {request.slug}")
        
        return JobResponse(
            job_id=task.id,
            status="queued"
        )
        
    except Exception as e:
        logger.error(f"Failed to create report task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue report task: {str(e)}"
        )


@router.get("/scopes")
async def list_report_scopes():
    """
    List available report scopes.
    
    Returns:
        Dict with available scopes and descriptions
    
    Example:
        GET /api/reports/scopes
        
        Response:
        {
            "scopes": [
                {
                    "name": "LIFETIME",
                    "description": "All available data"
                },
                ...
            ]
        }
    """
    return {
        "scopes": [
            {
                "name": "LIFETIME",
                "description": "All available data"
            },
            {
                "name": "LAST-7-DAYS",
                "description": "Last 7 days of data"
            },
            {
                "name": "LAST-30-DAYS",
                "description": "Last 30 days of data"
            },
            {
                "name": "2025-Q1",
                "description": "Quarter 1, 2025 (example)",
                "pattern": "YYYY-Qn"
            },
            {
                "name": "2025-01..2025-03",
                "description": "Custom date range (example)",
                "pattern": "YYYY-MM..YYYY-MM"
            }
        ]
    }

