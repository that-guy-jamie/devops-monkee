from __future__ import annotations

import os
from typing import Optional

import requests


class GHLClient:
    def __init__(self, api_key: Optional[str] = None, pit_token: Optional[str] = None, location_id: Optional[str] = None) -> None:
        # v1 key and v2 PIT token supported; prefer v2 when available
        self.api_key = api_key or os.getenv("GHL_API_KEY_PRIORITY")
        self.pit_token = pit_token or os.getenv("GHL_PIT_TOKEN")
        self.location_id = location_id or os.getenv("GHL_LOCATION_ID_PRIORITY")
        self.base_url_v1 = "https://rest.gohighlevel.com/v1"
        self.base_url_v2 = "https://services.leadconnectorhq.com"

        self.enabled = bool(self.location_id and (self.api_key or self.pit_token))

    def _headers_v1(self) -> dict:
        # Prefer dedicated v1 API key; fallback to PIT token if present
        token = self.api_key or self.pit_token
        if not token:
            raise RuntimeError("GHL API key not configured")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _headers_v2(self) -> dict:
        if not self.pit_token:
            raise RuntimeError("GHL PIT token not configured")
        return {
            "Authorization": f"Bearer {self.pit_token}",
            "Version": "2021-07-28",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def add_note(self, contact_id: str, body: str) -> None:
        if not self.enabled:
            return
        # Use v1 notes endpoint
        headers = self._headers_v1()
        payload = {
            "locationId": self.location_id,
            "note": body,
            "contactId": contact_id,
        }
        resp = requests.post(f"{self.base_url_v1}/notes/", headers=headers, json=payload, timeout=20)
        resp.raise_for_status()

    def list_custom_fields(self) -> dict:
        if not self.enabled:
            return {}
        # Prefer v2; on 401 fallback to v1
        # Try v2 endpoint variant 1: global custom-fields with locationId query
        headers = self._headers_v2()
        headers_with_loc = {**headers, "LocationId": self.location_id}
        url_list = [
            f"{self.base_url_v2}/custom-fields/?locationId={self.location_id}",
            f"{self.base_url_v2}/locations/{self.location_id}/customFields",
        ]
        last_exc: Exception | None = None
        for u in url_list:
            try:
                resp = requests.get(u, headers=headers_with_loc, timeout=25)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:  # noqa: BLE001
                last_exc = e

        # v1 fallback (supports API key or PIT token as bearer)
        headers_v1 = self._headers_v1()
        url_v1s = [
            f"{self.base_url_v1}/custom-fields/?locationId={self.location_id}",
            f"{self.base_url_v1}/customFields/?locationId={self.location_id}",
        ]
        last_exc = None
        for u in url_v1s:
            try:
                resp_v1 = requests.get(u, headers=headers_v1, timeout=25)
                resp_v1.raise_for_status()
                return resp_v1.json()
            except Exception as e:  # noqa: BLE001
                last_exc = e
        if last_exc:
            raise last_exc

    def list_opportunity_custom_fields(self) -> dict:
        # If separate endpoint emerges, switch here; for now reuse list_custom_fields
        return self.list_custom_fields()


