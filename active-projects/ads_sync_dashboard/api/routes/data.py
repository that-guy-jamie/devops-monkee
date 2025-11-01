"""
Data status API endpoints.

Handles querying data freshness and sync status from ads_sync state files.
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import logging

from api.models.responses import DataStatusResponse
from api.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("/status/{slug}", response_model=DataStatusResponse)
async def get_data_status(slug: str):
    """
    Get data freshness status for a client.
    
    Reads the state file from ads_sync to determine when data was last synced.
    
    Args:
        slug: Client slug (e.g., 'priority-roofing')
    
    Returns:
        DataStatusResponse with watermark and sync timestamps
    
    Raises:
        HTTPException: If state file not found or cannot be read
    
    Example:
        GET /api/data/status/priority-roofing
        
        Response:
        {
            "slug": "priority-roofing",
            "last_append_timestamp": "2025-10-13T08:00:00+00:00",
            "last_sync": "2025-10-13T08:00:00+00:00",
            "watermark_date": "2025-10-12"
        }
    """
    logger.debug(f"Fetching data status for {slug}")
    
    # Build path to state file
    ads_sync_path = settings.get_ads_sync_path()
    state_path = ads_sync_path / "state" / f"{slug}.json"
    
    logger.debug(f"State file path: {state_path}")
    
    if not state_path.exists():
        logger.warning(f"State file not found for {slug}: {state_path}")
        raise HTTPException(
            status_code=404,
            detail=f"No state found for client '{slug}'. Has sync been run yet?"
        )
    
    try:
        with open(state_path, 'r') as f:
            state = json.load(f)
        
        logger.debug(f"Loaded state for {slug}: {len(state)} keys")
        
        # Extract relevant fields
        response = DataStatusResponse(
            slug=slug,
            last_append_timestamp=state.get("last_updated"),
            last_sync=state.get("google_ads", {}).get("last_sync"),
            watermark_date=state.get("google_ads", {}).get("watermark_date")
        )
        
        return response
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in state file for {slug}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"State file is corrupted for '{slug}'"
        )
    
    except Exception as e:
        logger.error(f"Failed to read state for {slug}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read state file: {str(e)}"
        )


@router.get("/clients")
async def list_clients():
    """
    List all clients with available state files.
    
    Scans the ads_sync state directory to find all configured clients.
    
    Returns:
        Dict with list of client slugs and their basic info
    
    Example:
        GET /api/data/clients
        
        Response:
        {
            "clients": [
                {
                    "slug": "priority-roofing",
                    "has_state": true
                },
                {
                    "slug": "abe-lincoln-movers",
                    "has_state": true
                }
            ]
        }
    """
    logger.debug("Listing all clients")
    
    ads_sync_path = settings.get_ads_sync_path()
    state_dir = ads_sync_path / "state"
    
    if not state_dir.exists():
        logger.warning(f"State directory not found: {state_dir}")
        return {"clients": []}
    
    clients = []
    
    # Find all .json files in state directory
    for state_file in state_dir.glob("*.json"):
        slug = state_file.stem  # Filename without .json extension
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            clients.append({
                "slug": slug,
                "has_state": True,
                "watermark_date": state.get("google_ads", {}).get("watermark_date"),
                "last_updated": state.get("last_updated")
            })
            
        except Exception as e:
            logger.warning(f"Failed to read state for {slug}: {str(e)}")
            clients.append({
                "slug": slug,
                "has_state": True,
                "error": str(e)
            })
    
    logger.info(f"Found {len(clients)} clients with state files")
    
    return {"clients": clients}

