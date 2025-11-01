"""
Create Materialized Views
==========================

Creates the focus materialized views for efficient AI analysis.
These views pre-filter and cap data to keep prompts small and cheap.

Usage:
    poetry run python scripts/create_materialized_views.py
"""

import sys
from pathlib import Path

from sqlalchemy import text

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import sync_engine


def create_materialized_views():
    """Create materialized views from SQL file."""
    print("[CREATE VIEWS] Starting...")
    
    # Read SQL file
    sql_file = Path(__file__).parent.parent / "database" / "materialized_views.sql"
    print(f"[CREATE VIEWS] Reading SQL from: {sql_file}")
    
    if not sql_file.exists():
        print(f"[ERROR] SQL file not found: {sql_file}")
        sys.exit(1)
    
    sql_content = sql_file.read_text()
    
    # Execute SQL
    print("[CREATE VIEWS] Executing SQL...")
    with sync_engine.connect() as conn:
        # Execute the entire SQL file
        conn.execute(text(sql_content))
        conn.commit()
    
    print("[CREATE VIEWS] Materialized views created successfully!")
    print()
    print("Created views:")
    print("  - focus_keywords_30d")
    print("  - focus_search_terms_30d")
    print()
    print("To refresh these views, run:")
    print("  REFRESH MATERIALIZED VIEW focus_keywords_30d;")
    print("  REFRESH MATERIALIZED VIEW focus_search_terms_30d;")


def refresh_materialized_views():
    """Refresh existing materialized views."""
    print("[REFRESH VIEWS] Starting...")
    
    with sync_engine.connect() as conn:
        print("[REFRESH VIEWS] Refreshing focus_keywords_30d...")
        conn.execute(text("REFRESH MATERIALIZED VIEW focus_keywords_30d"))
        
        print("[REFRESH VIEWS] Refreshing focus_search_terms_30d...")
        conn.execute(text("REFRESH MATERIALIZED VIEW focus_search_terms_30d"))
        
        conn.commit()
    
    print("[REFRESH VIEWS] All views refreshed successfully!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage materialized views")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh existing views instead of creating them"
    )
    
    args = parser.parse_args()
    
    if args.refresh:
        refresh_materialized_views()
    else:
        create_materialized_views()

