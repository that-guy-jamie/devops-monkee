"""
Response models for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional


class JobResponse(BaseModel):
    """Response model for job creation."""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: Literal["queued", "started", "finished", "failed"] = Field(
        ...,
        description="Current job status"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "job_id": "abc123-def456-ghi789",
                    "status": "queued"
                }
            ]
        }
    }


class JobStatusResponse(BaseModel):
    """Response model for job status queries."""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: Literal["queued", "started", "finished", "failed"] = Field(
        ...,
        description="Current job status"
    )
    result: Optional[str] = Field(
        default=None,
        description="Job result (stdout from CLI) if completed successfully"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if job failed"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "job_id": "abc123-def456-ghi789",
                    "status": "finished",
                    "result": "Validation complete for 'priority-roofing'",
                    "error": None
                },
                {
                    "job_id": "xyz789-uvw456-rst123",
                    "status": "failed",
                    "result": None,
                    "error": "Client config not found: invalid-client"
                }
            ]
        }
    }


class DataStatusResponse(BaseModel):
    """Response model for data freshness status."""
    
    slug: str = Field(..., description="Client slug")
    last_append_timestamp: Optional[str] = Field(
        default=None,
        description="ISO timestamp of last state update"
    )
    last_sync: Optional[str] = Field(
        default=None,
        description="ISO timestamp of last successful sync"
    )
    watermark_date: Optional[str] = Field(
        default=None,
        description="Date of last synced data (YYYY-MM-DD)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "slug": "priority-roofing",
                    "last_append_timestamp": "2025-10-13T08:00:00Z",
                    "last_sync": "2025-10-13T08:00:00Z",
                    "watermark_date": "2025-10-12"
                }
            ]
        }
    }

