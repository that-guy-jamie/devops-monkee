"""
Request models for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional


class ExecuteRunbookRequest(BaseModel):
    """Request model for executing ads_sync CLI commands."""
    
    slug: str = Field(
        ...,
        description="Client slug (e.g., 'priority-roofing')",
        examples=["priority-roofing", "abe-lincoln-movers"]
    )
    command: Literal["init", "append", "validate", "repair", "force-unlock"] = Field(
        ...,
        description="CLI command to execute"
    )
    args: Optional[dict] = Field(
        default=None,
        description="Additional command arguments (e.g., start/end dates for repair)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "slug": "priority-roofing",
                    "command": "validate"
                },
                {
                    "slug": "priority-roofing",
                    "command": "repair",
                    "args": {
                        "start": "2025-09-01",
                        "end": "2025-09-30"
                    }
                }
            ]
        }
    }


class GenerateReportRequest(BaseModel):
    """Request model for generating reports."""
    
    slug: str = Field(
        ...,
        description="Client slug",
        examples=["priority-roofing"]
    )
    scope: str = Field(
        default="LAST-30-DAYS",
        description="Report scope (LIFETIME, LAST-7-DAYS, LAST-30-DAYS, 2025-Q3, etc.)",
        examples=["LIFETIME", "LAST-30-DAYS", "2025-Q3"]
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "slug": "priority-roofing",
                    "scope": "LAST-30-DAYS"
                },
                {
                    "slug": "abe-lincoln-movers",
                    "scope": "LIFETIME"
                }
            ]
        }
    }

