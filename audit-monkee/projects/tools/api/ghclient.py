import httpx, os
from typing import Dict, Any, Optional, List

BASE_URL = os.getenv('GHL_BASE_URL', 'https://services.leadconnectorhq.com')
API_VERSION_DEFAULT = '2021-07-28'

class GHLClient:
    def __init__(self, access_token: Optional[str] = None, version: str = API_VERSION_DEFAULT):
        self.access_token = access_token or os.getenv('GHL_ACCESS_TOKEN')
        self.version = version

        if not self.access_token:
            raise RuntimeError('GHL access token not configured (set GHL_ACCESS_TOKEN env var)')

        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Version": self.version
        }

    # Contacts: Create a Note
    # POST /contacts/:contactId/notes
    def create_contact_note(self, contact_id: str, body: str) -> Dict[str, Any]:
        url = f"{BASE_URL}/contacts/{contact_id}/notes"
        payload = { "body": body }
        r = httpx.post(url, headers=self.headers, json=payload, timeout=30.0)
        r.raise_for_status()
        return r.json()

    # Contacts: Upsert (useful for setting custom fields)
    # POST /contacts/upsert
    def upsert_contact_custom_fields(self, location_id: str, contact_id: str, custom_fields: Dict[str, Any]) -> Dict[str, Any]:
        cf_array = []
        for key, value in custom_fields.items():
            cf_array.append({
                "key": key,
                "field_value": value
            })
        payload = {
            "id": contact_id,
            "locationId": location_id,
            "customFields": cf_array,
            "source": "audit-monkee"
        }
        url = f"{BASE_URL}/contacts/upsert"
        r = httpx.post(url, headers=self.headers, json=payload, timeout=30.0)
        r.raise_for_status()
        return r.json()

    # (Optional) Media upload -> returns URL to store in a file-type custom field.
    # POST /medias/upload
    def upload_media(self, file_path: str, name: Optional[str] = None) -> Dict[str, Any]:
        up_headers = self.headers.copy()
        up_headers.pop('Accept', None)
        up_headers['Version'] = '2021-07-28'
        with open(file_path, 'rb') as f:
            files = {
                "file": (name or os.path.basename(file_path), f, "application/octet-stream")
            }
            r = httpx.post(f"{BASE_URL}/medias/upload", headers=up_headers, files=files, timeout=60.0)
            r.raise_for_status()
            return r.json()
