"""
Report Generation and GHL Integration API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import logging

from backend.database import SyncSessionLocal
from backend.services.report_generator import generate_client_report, ReportGenerator
from backend.services.ghl_file_upload import upload_report_to_ghl
from backend.models.client import Client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate/{client_id}")
async def generate_report(
    client_id: int,
    analysis_id: Optional[int] = None,
    background_tasks: BackgroundTasks = None
):
    """Generate a client report."""
    try:
        # Verify client exists
        db = SyncSessionLocal()
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail=f"Client {client_id} not found")

        # Generate report
        report_bytes = generate_client_report(client_id, analysis_id)

        # Save to temporary file
        generator = ReportGenerator(db)
        file_path = generator.save_report_to_file(client_id, report_bytes)

        return {
            "success": True,
            "client_id": client_id,
            "file_path": file_path,
            "message": "Report generated successfully"
        }

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-and-upload/{client_id}")
async def generate_and_upload_report(
    client_id: int,
    contact_id: str,
    analysis_id: Optional[int] = None,
    custom_field: str = "ads_monkee_report",
    background_tasks: BackgroundTasks = None
):
    """Generate a client report and upload to GHL."""
    try:
        # Verify client exists
        db = SyncSessionLocal()
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail=f"Client {client_id} not found")

        # Generate report
        report_bytes = generate_client_report(client_id, analysis_id)

        # Save to temporary file
        generator = ReportGenerator(db)
        file_path = generator.save_report_to_file(client_id, report_bytes)

        # Upload to GHL
        upload_result = upload_report_to_ghl(contact_id, file_path, custom_field)

        return {
            "success": upload_result["success"],
            "client_id": client_id,
            "contact_id": contact_id,
            "upload_result": upload_result,
            "message": "Report generated and uploaded to GHL"
        }

    except Exception as e:
        logger.error(f"Report generation and upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-to-ghl")
async def upload_existing_report(
    contact_id: str,
    file_path: str,
    custom_field: str = "ads_monkee_report"
):
    """Upload an existing report file to GHL."""
    try:
        upload_result = upload_report_to_ghl(contact_id, file_path, custom_field)

        return {
            "success": upload_result["success"],
            "contact_id": contact_id,
            "upload_result": upload_result,
            "message": "Report uploaded to GHL"
        }

    except Exception as e:
        logger.error(f"Report upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
