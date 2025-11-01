"""
GoHighLevel File Upload Service for Ads Monkee

Handles uploading generated reports to GHL custom file fields and triggering automations.
"""
import os
import requests
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class GHLFileUploadService:
    """Service for uploading files to GoHighLevel and triggering automations."""

    def __init__(self):
        self.pit_token = os.getenv("GHL_PIT_TOKEN")
        self.location_id = os.getenv("GHL_LOCATION_ID_PRIORITY")
        self.base_url = "https://services.leadconnectorhq.com"

        if not self.pit_token or not self.location_id:
            logger.warning("GHL credentials not configured - file upload disabled")
            self.enabled = False
        else:
            self.enabled = True

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for GHL API."""
        if not self.enabled:
            raise RuntimeError("GHL service not configured")

        return {
            "Authorization": f"Bearer {self.pit_token}",
            "Version": "2021-07-28",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def upload_file_to_media_library(self, file_path: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a file to GHL media library.

        Args:
            file_path: Path to the file to upload
            name: Optional name for the file

        Returns:
            API response data with file ID and URL
        """
        if not self.enabled:
            logger.info(f"GHL upload disabled - would upload {file_path}")
            return {"success": False, "message": "GHL service disabled"}

        try:
            # Read file
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Prepare multipart form data
            files = {
                'file': (file_path_obj.name, file_data, 'application/pdf')
            }

            if name:
                files['name'] = (None, name)

            # Upload file to media library
            upload_url = f"{self.base_url}/medias/upload-file"
            headers = self._get_headers()
            # Remove Content-Type for multipart upload
            headers.pop("Content-Type", None)

            response = requests.post(
                upload_url,
                headers=headers,
                files=files,
                timeout=60  # Longer timeout for file uploads
            )

            response.raise_for_status()
            result = response.json()

            logger.info(f"Successfully uploaded file to GHL media library: {result.get('id')}")
            return {
                "success": True,
                "file_id": result.get("id"),
                "file_url": result.get("url"),
                "name": result.get("name"),
                "message": "File uploaded to media library successfully"
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"GHL media upload failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "File upload failed"
            }
        except Exception as e:
            logger.error(f"Unexpected error during GHL media upload: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Unexpected error"
            }

    def update_contact_custom_field(self, contact_id: str, field_name: str, file_url: str) -> Dict[str, Any]:
        """
        Update a contact's custom field with a file URL.

        Args:
            contact_id: GHL contact ID
            field_name: Name of the custom field
            file_url: URL of the uploaded file

        Returns:
            API response data
        """
        if not self.enabled:
            logger.info(f"GHL field update disabled - would update {field_name} for contact {contact_id}")
            return {"success": False, "message": "GHL service disabled"}

        try:
            # Update contact custom field
            update_url = f"{self.base_url}/contacts/{contact_id}"
            headers = self._get_headers()

            payload = {
                "customFields": [
                    {
                        "key": field_name,
                        "field_value": file_url
                    }
                ]
            }

            response = requests.put(
                update_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            logger.info(f"Successfully updated custom field {field_name} for contact {contact_id}")
            return {
                "success": True,
                "contact_id": result.get("id"),
                "message": "Custom field updated successfully"
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"GHL custom field update failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Custom field update failed"
            }
        except Exception as e:
            logger.error(f"Unexpected error during GHL field update: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Unexpected error"
            }

    def upload_report_and_trigger_automation(self, contact_id: str, report_path: str,
                                           custom_field: str = "ads_monkee_report") -> Dict[str, Any]:
        """
        Upload a report file to media library and update contact's custom field to trigger automation.

        Args:
            contact_id: GHL contact ID
            report_path: Path to the PDF report file
            custom_field: Name of the custom field to update

        Returns:
            Combined result of upload and field update
        """
        # Step 1: Upload file to media library
        upload_result = self.upload_file_to_media_library(report_path)

        if not upload_result["success"]:
            return upload_result

        # Step 2: Update custom field with file URL (this should trigger automation)
        field_result = self.update_contact_custom_field(
            contact_id,
            custom_field,
            upload_result["file_url"]
        )

        # Combine results
        return {
            "success": upload_result["success"] and field_result["success"],
            "upload_result": upload_result,
            "field_result": field_result,
            "file_url": upload_result.get("file_url"),
            "message": "Report uploaded to media library and contact field updated"
        }

    def get_contact_custom_fields(self, contact_id: str) -> Dict[str, Any]:
        """
        Get a contact's custom fields to check current values.

        Args:
            contact_id: GHL contact ID

        Returns:
            Contact custom fields data
        """
        if not self.enabled:
            return {"customFields": []}

        try:
            url = f"{self.base_url}/contacts/{contact_id}"
            headers = self._get_headers()

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            contact_data = response.json()
            return contact_data.get("customFields", {})

        except Exception as e:
            logger.error(f"Failed to get contact custom fields: {e}")
            return {"customFields": [], "error": str(e)}


def upload_report_to_ghl(contact_id: str, report_path: str, custom_field: str = "ads_monkee_report") -> Dict[str, Any]:
    """Upload a report to GHL and trigger automation."""
    service = GHLFileUploadService()
    return service.upload_report_and_trigger_automation(contact_id, report_path, custom_field)
