#!/usr/bin/env python3
"""
Query GoHighLevel custom fields for Priority Roofing location.
"""
import os
import json
import requests
from typing import Dict, List, Any

def query_priority_custom_fields() -> Dict[str, Any]:
    """Query custom fields for Priority Roofing location."""
    pit_token = os.getenv("GHL_PIT_TOKEN")
    location_id = os.getenv("GHL_LOCATION_ID_PRIORITY")

    if not pit_token or not location_id:
        print("GHL_PIT_TOKEN and GHL_LOCATION_ID_PRIORITY must be set")
        return {}

    base_url = "https://services.leadconnectorhq.com"
    headers = {
        "Authorization": f"Bearer {pit_token}",
        "Version": "2021-07-28",
        "Accept": "application/json",
    }

    try:
        # Query custom fields for Priority Roofing location
        print(f"Querying custom fields for location: {location_id}")

        # Get all custom fields - try with model=all first
        try:
            response = requests.get(
                f"{base_url}/locations/{location_id}/customFields?model=all",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
        except:
            # Try without model parameter
            response = requests.get(
                f"{base_url}/locations/{location_id}/customFields",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

        custom_fields = response.json()
        print(f"Found {len(custom_fields.get('customFields', []))} custom fields")

        # Display custom fields
        for field in custom_fields.get('customFields', []):
            print(f"  ID: {field['id']}")
            print(f"  Name: {field['name']}")
            print(f"  Type: {field['type']}")
            print(f"  Model: {field.get('model', 'N/A')}")
            print("  ---")

        return custom_fields

    except Exception as e:
        print(f"Error querying custom fields: {e}")
        return {}

def main():
    """Main function."""
    print("[INFO] Querying GoHighLevel Custom Fields for Priority Roofing")
    print("=" * 60)

    custom_fields = query_priority_custom_fields()

    if custom_fields:
        print(f"\n[SUCCESS] Successfully retrieved {len(custom_fields.get('customFields', []))} custom fields")

        # Save to file for reference
        with open(".cursor/.agent-tools/priority_ghl_custom_fields.json", "w") as f:
            json.dump(custom_fields, f, indent=2)
        print("[INFO] Saved to: .cursor/.agent-tools/priority_ghl_custom_fields.json")

        # Look for file upload fields
        file_fields = [f for f in custom_fields.get('customFields', []) if f.get('type') == 'file']
        if file_fields:
            print(f"\n[INFO] Found {len(file_fields)} file upload fields:")
            for field in file_fields:
                print(f"  {field['name']} (ID: {field['id']})")
        else:
            print("\n[WARNING] No file upload custom fields found")
    else:
        print("\n[ERROR] No custom fields found or API error")

if __name__ == "__main__":
    main()
