"""
Client Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from backend.database import SyncSessionLocal
from backend.models.client import Client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_clients():
    """Get all clients."""
    try:
        db = SyncSessionLocal()
        clients = db.query(Client).all()
        
        # Convert to dict format for frontend
        client_data = []
        for client in clients:
            client_data.append({
                "id": client.id,
                "name": client.name,
                "slug": client.slug,
                "status": client.status,
                "google_ads_customer_id": client.google_ads_customer_id,
                "google_ads_account_name": client.google_ads_account_name,
                "ghl_location_id": client.ghl_location_id,
                "ghl_contact_id": client.ghl_contact_id,
                "last_sync_at": client.last_sync_at.isoformat() if client.last_sync_at else None,
                "last_analysis_at": client.last_analysis_at.isoformat() if client.last_analysis_at else None,
                "created_at": client.created_at.isoformat(),
                "updated_at": client.updated_at.isoformat(),
            })
        
        return client_data
        
    except Exception as e:
        logger.error(f"Failed to get clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}")
async def get_client(client_id: int):
    """Get specific client by ID."""
    try:
        db = SyncSessionLocal()
        client = db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
        
        return {
            "id": client.id,
            "name": client.name,
            "slug": client.slug,
            "status": client.status,
            "google_ads_customer_id": client.google_ads_customer_id,
            "google_ads_account_name": client.google_ads_account_name,
            "ghl_location_id": client.ghl_location_id,
            "ghl_contact_id": client.ghl_contact_id,
            "last_sync_at": client.last_sync_at.isoformat() if client.last_sync_at else None,
            "last_analysis_at": client.last_analysis_at.isoformat() if client.last_analysis_at else None,
            "created_at": client.created_at.isoformat(),
            "updated_at": client.updated_at.isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
