"""
Analysis API Router
===================

Endpoints for triggering and monitoring AI analysis runs.
Implements the 202 Accepted pattern per architecture.
"""

from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_sync_db
from backend.models import AnalysisRun, AnalysisRunStatus, Client
from backend.schemas.analysis import (
    AnalysisRunCreate,
    AnalysisRunResult,
    AnalysisRunStatus as AnalysisRunStatusSchema,
    Synthesis,
)
from backend.tasks.analysis import run_full_analysis

router = APIRouter(prefix="/analysis", tags=["Analysis"])


# ==============================================================================
# POST /clients/{client_id}/analyze - Trigger Analysis
# ==============================================================================

@router.post(
    "/clients/{client_id}/analyze",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=dict,
)
def trigger_analysis(
    client_id: int,
    request: Optional[AnalysisRunCreate] = None,
    db: Session = Depends(get_sync_db),
):
    """
    Trigger a new analysis run for a client.
    
    Returns 202 Accepted immediately with a run_id.
    The actual analysis runs asynchronously via Celery.
    
    Args:
        client_id: Client ID to analyze
        request: Optional analysis configuration
        db: Database session
    
    Returns:
        {"run_id": "uuid", "status": "queued"}
    """
    # Validate client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client {client_id} not found",
        )
    
    # Parse request
    if request is None:
        request = AnalysisRunCreate(client_id=client_id)
    
    # Check for recent cached run (if not force_refresh)
    if not request.force_refresh:
        # TODO (Week 2): Implement cache lookup by feature_hash + prompt_version
        # For now, always run fresh
        pass
    
    # Create analysis run record
    run_id = uuid4()
    run = AnalysisRun(
        run_id=run_id,
        client_id=client_id,
        window_days=request.window_days,
        status=AnalysisRunStatus.QUEUED,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    
    # Enqueue Celery task
    run_full_analysis(
        client_id=client_id,
        run_id=str(run_id),
        window_days=request.window_days,
    )
    
    return {
        "run_id": str(run_id),
        "status": "queued",
        "message": f"Analysis started for {client.name}",
    }


# ==============================================================================
# GET /analysis/{run_id} - Get Analysis Status/Results
# ==============================================================================

@router.get(
    "/{run_id}",
    response_model=AnalysisRunResult,
)
def get_analysis_run(
    run_id: UUID,
    db: Session = Depends(get_sync_db),
):
    """
    Get the status and results of an analysis run.
    
    Returns:
        - If status=queued/running: Just status and progress
        - If status=done: Full results (JSON + Markdown)
        - If status=error: Error details
    
    Args:
        run_id: Analysis run UUID
        db: Database session
    
    Returns:
        AnalysisRunResult with status and results (if complete)
    """
    # Get run
    run = db.query(AnalysisRun).filter(AnalysisRun.run_id == run_id).first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis run {run_id} not found",
        )
    
    # Build response
    result = AnalysisRunResult(
        run_id=run.run_id,
        client_id=run.client_id,
        status=run.status.value,
        started_at=run.started_at,
        finished_at=run.finished_at,
        duration_seconds=run.duration_seconds,
    )
    
    # If done, include results
    if run.status == AnalysisRunStatus.DONE and run.report:
        result.result_json = Synthesis(**run.report.json)
        result.markdown = run.report.markdown
        result.model = run.model
        result.prompt_version = run.prompt_version
        result.cost = {
            "input_tokens": run.input_tokens,
            "output_tokens": run.output_tokens,
            "usd": float(run.cost_usd) if run.cost_usd else None,
        }
    
    # If error, include error message
    if run.status == AnalysisRunStatus.ERROR:
        result.error = run.error
    
    return result


# ==============================================================================
# GET /clients/{client_id}/analyses - List Client Analyses
# ==============================================================================

@router.get(
    "/clients/{client_id}/analyses",
    response_model=list[AnalysisRunStatusSchema],
)
def list_client_analyses(
    client_id: int,
    limit: int = 10,
    db: Session = Depends(get_sync_db),
):
    """
    List recent analysis runs for a client.
    
    Args:
        client_id: Client ID
        limit: Maximum number of runs to return
        db: Database session
    
    Returns:
        List of AnalysisRunStatus objects
    """
    # Validate client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client {client_id} not found",
        )
    
    # Get recent runs
    runs = (
        db.query(AnalysisRun)
        .filter(AnalysisRun.client_id == client_id)
        .order_by(AnalysisRun.created_at.desc())
        .limit(limit)
        .all()
    )
    
    # Build response
    return [
        AnalysisRunStatusSchema(
            run_id=run.run_id,
            client_id=run.client_id,
            status=run.status.value,
            started_at=run.started_at,
            finished_at=run.finished_at,
            error=run.error,
            current_phase=run.current_phase.value if run.current_phase else None,
            progress_pct=run.progress_pct,
        )
        for run in runs
    ]

