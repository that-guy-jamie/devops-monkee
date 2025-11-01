#!/usr/bin/env python3
"""
Query GoHighLevel locations using agency account access.
"""
import os
import json
import requests
from typing import Dict, List, Any

def query_ghl_locations() -> List[Dict[str, Any]]:
    """Query all GHL locations accessible from agency account."""
    pit_token = os.getenv("GHL_PIT_TOKEN")
    api_key = os.getenv("GHL_API_KEY_PRIORITY")

    if not pit_token and not api_key:
        print("Neither GHL_PIT_TOKEN nor GHL_API_KEY_PRIORITY configured")
        return []

    base_url = "https://services.leadconnectorhq.com"

    # Try PIT token first, then API key
    auth_token = pit_token or api_key
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Version": "2021-07-28",
        "Accept": "application/json",
    }

    try:
        # Query locations using search endpoint
        response = requests.get(f"{base_url}/locations/search", headers=headers, timeout=30)
        response.raise_for_status()

        locations = response.json().get("locations", [])
        print(f"Found {len(locations)} GHL locations:")

        for location in locations:
            print(f"  ID: {location['id']}")
            print(f"  Name: {location.get('name', 'N/A')}")
            print(f"  Address: {location.get('address', {}).get('city', 'N/A')}")
            print("  ---")

        return locations

    except Exception as e:
        print(f"Error querying GHL locations: {e}")
        return []

def main():
    """Main function."""
    print("[INFO] Querying GoHighLevel Locations (Agency Access)")
    print("=" * 50)

    locations = query_ghl_locations()

    if locations:
        print(f"\n[SUCCESS] Successfully retrieved {len(locations)} locations")
        print("\n[INFO] Location IDs for client configuration:")
        for loc in locations:
            print(f"  {loc['id']} - {loc.get('name', 'Unnamed Location')}")

        # Save to file for reference
        with open(".cursor/.agent-tools/ghl_locations.json", "w") as f:
            json.dump(locations, f, indent=2)
        print("\n[INFO] Saved to: .cursor/.agent-tools/ghl_locations.json")
    else:
        print("\n[ERROR] No locations found or API error")

if __name__ == "__main__":
    main()
