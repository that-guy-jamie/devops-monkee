#!/usr/bin/env python3
"""
Test script for Ads Monkee report generation and GHL integration.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.report_generator import generate_client_report, ReportGenerator
from backend.services.ghl_file_upload import upload_report_to_ghl
from backend.database import SyncSessionLocal


def test_report_generation():
    """Test report generation functionality."""
    print("[TEST] Testing Ads Monkee Report Generation...")

    try:
        # Get database session
        db = SyncSessionLocal()

        # Test with a sample client (assuming client ID 1 exists)
        client_id = 1

        print(f"[INFO] Generating report for client {client_id}...")

        # Generate report
        report_bytes = generate_client_report(client_id)

        print(f"[SUCCESS] Report generated successfully ({len(report_bytes)} bytes)")

        # Save to file
        generator = ReportGenerator(db)
        file_path = generator.save_report_to_file(client_id, report_bytes)

        print(f"[INFO] Report saved to: {file_path}")

        # Test GHL upload (if credentials are configured)
        try:
            # This would normally use the actual contact ID from the database
            # For testing, we'll just show what would happen
            print("[INFO] GHL upload would be triggered here...")
            print("   (Requires GHL_PIT_TOKEN and GHL_LOCATION_ID_PRIORITY environment variables)")

        except Exception as e:
            print(f"[WARNING] GHL upload test skipped: {e}")

        return True

    except Exception as e:
        print(f"[ERROR] Report generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("[INFO] Ads Monkee Report Generation Test Suite")
    print("=" * 50)

    success = test_report_generation()

    print("=" * 50)
    if success:
        print("[SUCCESS] All tests passed!")
        print("\n[INFO] Next Steps:")
        print("1. Set up Google test account credentials")
        print("2. Configure GHL integration with real contact IDs")
        print("3. Test end-to-end report generation and delivery")
    else:
        print("[ERROR] Some tests failed!")
        print("Check the error messages above for details.")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
