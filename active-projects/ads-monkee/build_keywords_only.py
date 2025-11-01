"""Build only keywords and search terms aggregates"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.build_aggregates import build_keyword_aggregates, build_search_term_aggregates

print("[BUILD] Starting keywords and search terms only...")
start = datetime.now()

try:
    build_keyword_aggregates(180)
    build_search_term_aggregates(180)
    
    duration = (datetime.now() - start).total_seconds()
    print(f"\n[BUILD] Complete in {duration:.1f}s!")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

