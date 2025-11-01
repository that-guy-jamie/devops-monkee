#!/usr/bin/env python3
"""
Check the 5 supposedly "no-data" clients to verify if they actually have data.
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

clients = [
    'customer-248-649-3690',
    'customer-854-315-6147',
    'customer-629-150-4682',
    'customer-776-663-1064',
    'customer-512-678-0705'
]

print("\n" + "="*70)
print("  NO-DATA CLIENTS INVESTIGATION")
print("="*70 + "\n")

for client in clients:
    csv_path = DATA_DIR / client / f"{client}-master-campaign_data.csv"
    
    if not csv_path.exists():
        print(f"\n{client}:")
        print(f"  [ERROR] CSV file not found!")
        continue
    
    df = pd.read_csv(csv_path)
    
    print(f"\n{client}:")
    print(f"  Rows:        {len(df):,}")
    print(f"  Campaigns:   {df['campaign_name'].nunique()}")
    print(f"  Impressions: {df['impressions'].sum():,}")
    print(f"  Clicks:      {df['clicks'].sum():,}")
    print(f"  Cost:        ${df['cost'].sum():,.2f}")
    print(f"  Conversions: {df['conversions'].sum():.1f}")
    
    # Check if truly "no data"
    has_data = (df['impressions'].sum() > 0 or 
                df['clicks'].sum() > 0 or 
                df['cost'].sum() > 0)
    
    if has_data:
        print(f"  Status:      ✓ HAS DATA")
    else:
        print(f"  Status:      ✗ NO DATA (all zeros)")

print("\n" + "="*70 + "\n")

