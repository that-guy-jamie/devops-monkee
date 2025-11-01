"""
Runbook execution API endpoints.

Handles triggering CLI command execution via Celery job queue.
"""

from fastapi import APIRouter, HTTPException
import logging

from api.models.requests import ExecuteRunbookRequest
from api.models.responses import JobResponse
from api.config import settings
from worker.tasks import execute_cli_command

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/runbooks", tags=["runbooks"])


@router.post("/execute", response_model=JobResponse)
async def execute_runbook(request: ExecuteRunbookRequest):
    """
    Execute an ads_sync CLI command as a background job.
    
    This endpoint queues the command for execution and immediately returns a job ID.
    The command runs asynchronously in the background worker.
    
    Args:
        request: Runbook execution request with command and slug
    
    Returns:
        JobResponse with job_id and initial status
    
    Raises:
        HTTPException: If Redis connection fails or job creation fails
    
    Example:
        POST /api/runbooks/execute
        {
            "slug": "priority-roofing",
            "command": "validate"
        }
        
        Response:
        {
            "job_id": "abc123-def456",
            "status": "queued"
        }
    """
    logger.info(f"Received runbook execution request: {request.command} for {request.slug}")
    
    try:
        # Enqueue the CLI command using Celery
        task = execute_cli_command.apply_async(
            kwargs={
                'command': request.command,
                'slug': request.slug,
                **(request.args or {})
            }
        )
        
        logger.info(f"Celery task created: {task.id} for {request.command} {request.slug}")
        
        return JobResponse(
            job_id=task.id,
            status="queued"
        )
        
    except Exception as e:
        logger.error(f"Failed to create task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue task: {str(e)}"
        )


@router.get("/commands")
async def list_commands():
    """
    List available CLI commands.
    
    Returns:
        Dict with available commands and descriptions
    
    Example:
        GET /api/runbooks/commands
        
        Response:
        {
            "commands": [
                {
                    "name": "validate",
                    "description": "Validate client configuration"
                },
                ...
            ]
        }
    """
    return {
        "commands": [
            {
                "name": "init",
                "description": "Initialize historical data backfill (one-time)",
                "requires_args": False
            },
            {
                "name": "append",
                "description": "Perform incremental data sync",
                "requires_args": False
            },
            {
                "name": "validate",
                "description": "Validate client configuration and data",
                "requires_args": False
            },
            {
                "name": "repair",
                "description": "Repair data gaps for a date range",
                "requires_args": True,
                "args": ["start", "end"]
            },
            {
                "name": "force-unlock",
                "description": "Manually remove lock file",
                "requires_args": False
            }
        ]
    }

