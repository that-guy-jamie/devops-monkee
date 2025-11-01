"""
Job status API endpoints.

Handles querying status of background jobs.
"""

from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
import logging

from api.models.responses import JobStatusResponse
from api.config import settings
from worker.tasks import celery_app

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a background job.
    
    This endpoint allows polling for job completion and retrieving results.
    
    Args:
        job_id: Unique job identifier returned from execute endpoints
    
    Returns:
        JobStatusResponse with current status, result, and error info
    
    Raises:
        HTTPException: If job not found or Redis connection fails
    
    Example:
        GET /api/jobs/abc123-def456/status
        
        Response (queued):
        {
            "job_id": "abc123-def456",
            "status": "queued",
            "result": null,
            "error": null
        }
        
        Response (finished):
        {
            "job_id": "abc123-def456",
            "status": "finished",
            "result": "Validation complete for 'priority-roofing'",
            "error": null
        }
        
        Response (failed):
        {
            "job_id": "abc123-def456",
            "status": "failed",
            "result": null,
            "error": "CLI command failed: Config file not found"
        }
    """
    logger.debug(f"Fetching status for task {job_id}")
    
    try:
        # Get task result from Celery
        task = AsyncResult(job_id, app=celery_app)
        
        # Map Celery states to our API status
        status_map = {
            "PENDING": "queued",
            "STARTED": "started",
            "SUCCESS": "finished",
            "FAILURE": "failed",
            "RETRY": "started",
            "REVOKED": "failed"
        }
        
        task_status = status_map.get(task.state, "queued")
        
        # Extract result or error
        result = None
        error = None
        
        if task.state == "SUCCESS":
            # Task completed successfully
            if task.result:
                # Extract stdout from result dict
                if isinstance(task.result, dict):
                    result = task.result.get("stdout", str(task.result))
                else:
                    result = str(task.result)
        
        elif task.state == "FAILURE":
            # Task failed
            if task.info:
                error = str(task.info)
            else:
                error = "Task failed with unknown error"
        
        logger.debug(f"Task {job_id} status: {task_status}")
        
        return JobStatusResponse(
            job_id=job_id,
            status=task_status,
            result=result,
            error=error
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch task {job_id}: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Task not found or error occurred: {job_id}"
        )


@router.get("/{job_id}/result")
async def get_job_result(job_id: str):
    """
    Get the full result of a completed job.
    
    Returns the complete result object including stdout, stderr, and exit code.
    
    Args:
        job_id: Unique job identifier
    
    Returns:
        Dict with full job result
    
    Raises:
        HTTPException: If job not found, not finished, or failed
    
    Example:
        GET /api/jobs/abc123-def456/result
        
        Response:
        {
            "stdout": "...",
            "stderr": "",
            "exit_code": 0,
            "command": "validate",
            "slug": "priority-roofing",
            "args": {}
        }
    """
    logger.debug(f"Fetching full result for task {job_id}")
    
    try:
        # Get task result from Celery
        task = AsyncResult(job_id, app=celery_app)
        
    except Exception as e:
        logger.error(f"Failed to fetch task {job_id}: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Task not found: {job_id}"
        )
    
    if task.state != "SUCCESS":
        raise HTTPException(
            status_code=400,
            detail=f"Task is not finished successfully yet (status: {task.state})"
        )
    
    return task.result

