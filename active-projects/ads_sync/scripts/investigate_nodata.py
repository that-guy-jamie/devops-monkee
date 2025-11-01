#!/usr/bin/env python3
"""Investigate the 5 supposedly 'no-data' clients."""

import pandas as pd
import sys
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

results = []

print("\n" + "="*80)
print("  NO-DATA CLIENTS INVESTIGATION")
print("="*80)

for client in clients:
    csv_path = DATA_DIR / client / f"{client}-master-campaign_data.csv"
    
    if not csv_path.exists():
        result = {
            'client': client,
            'status': 'FILE NOT FOUND',
            'rows': 0,
            'campaigns': 0,
            'impressions': 0,
            'clicks': 0,
            'cost': 0.0,
            'conversions': 0.0
        }
        results.append(result)
        continue
    
    try:
        df = pd.read_csv(csv_path)
        
        result = {
            'client': client,
            'status': 'OK',
            'rows': len(df),
            'campaigns': df['campaign_name'].nunique() if len(df) > 0 else 0,
            'impressions': int(df['impressions'].sum()) if len(df) > 0 else 0,
            'clicks': int(df['clicks'].sum()) if len(df) > 0 else 0,
            'cost': float(df['cost'].sum()) if len(df) > 0 else 0.0,
            'conversions': float(df['conversions'].sum()) if len(df) > 0 else 0.0
        }
        
        # Determine if has data
        has_data = (result['impressions'] > 0 or 
                   result['clicks'] > 0 or 
                   result['cost'] > 0)
        result['has_data'] = has_data
        results.append(result)
        
    except Exception as e:
        result = {
            'client': client,
            'status': f'ERROR: {str(e)}',
            'rows': 0,
            'campaigns': 0,
            'impressions': 0,
            'clicks': 0,
            'cost': 0.0,
            'conversions': 0.0,
            'has_data': False
        }
        results.append(result)

# Print results
print()
for r in results:
    print(f"\n{r['client']}:")
    print(f"  Status:      {r['status']}")
    if r['status'] == 'OK':
        print(f"  Rows:        {r['rows']:,}")
        print(f"  Campaigns:   {r['campaigns']}")
        print(f"  Impressions: {r['impressions']:,}")
        print(f"  Clicks:      {r['clicks']:,}")
        print(f"  Cost:        ${r['cost']:,.2f}")
        print(f"  Conversions: {r['conversions']:.1f}")
        print(f"  Has Data:    {'YES' if r.get('has_data', False) else 'NO'}")

# Summary
print("\n" + "="*80)
print("SUMMARY:")
print("="*80)
has_data_count = sum(1 for r in results if r.get('has_data', False))
no_data_count = len(results) - has_data_count
print(f"  Clients with data: {has_data_count}")
print(f"  Clients with NO data: {no_data_count}")
print()

# Write to file
output_file = BASE_DIR / "NO-DATA-CLIENTS-INVESTIGATION.md"
with open(output_file, 'w') as f:
    f.write("# No-Data Clients Investigation\n\n")
    f.write("**Date:** 2025-10-15\n\n")
    f.write("## Results\n\n")
    
    for r in results:
        f.write(f"### {r['client']}\n\n")
        f.write(f"- **Status:** {r['status']}\n")
        if r['status'] == 'OK':
            f.write(f"- **Rows:** {r['rows']:,}\n")
            f.write(f"- **Campaigns:** {r['campaigns']}\n")
            f.write(f"- **Impressions:** {r['impressions']:,}\n")
            f.write(f"- **Clicks:** {r['clicks']:,}\n")
            f.write(f"- **Cost:** ${r['cost']:,.2f}\n")
            f.write(f"- **Conversions:** {r['conversions']:.1f}\n")
            f.write(f"- **Has Data:** {'✓ YES' if r.get('has_data', False) else '✗ NO (all zeros)'}\n")
        f.write("\n")
    
    f.write("## Summary\n\n")
    f.write(f"- **Clients with data:** {has_data_count}\n")
    f.write(f"- **Clients with NO data:** {no_data_count}\n\n")
    
    f.write("## Recommendations\n\n")
    for r in results:
        if not r.get('has_data', False) and r['status'] == 'OK':
            f.write(f"- **{r['client']}:** Verify account status in Google Ads UI, may be inactive or test account\n")

print(f"Report written to: {output_file}")
print()

