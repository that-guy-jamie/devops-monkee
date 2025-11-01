#!/usr/bin/env python3
"""
Quick script to analyze pulled campaign data.
"""
import pandas as pd
import sys
from pathlib import Path

def analyze_client_data(slug):
    data_file = Path(f"data/{slug}/{slug}-master-campaign_data.csv")
    
    if not data_file.exists():
        print(f"[ERROR] Data file not found: {data_file}")
        sys.exit(1)
    
    df = pd.read_csv(data_file)
    
    print(f"\n{'='*70}")
    print(f"  {slug.upper().replace('-', ' ')} - DATA SUMMARY")
    print(f"{'='*70}\n")
    
    print(f"[DATA OVERVIEW]")
    print(f"   Total Rows: {len(df):,}")
    print(f"   Date Range: {df['date'].min()} to {df['date'].max()}")
    print(f"   Unique Campaigns: {df['campaign_name'].nunique()}")
    
    print(f"\n[CAMPAIGN PERFORMANCE - 1 YEAR]")
    print(f"   Impressions:  {df['impressions'].sum():>15,}")
    print(f"   Clicks:       {df['clicks'].sum():>15,}")
    print(f"   Cost:         ${df['cost'].sum():>14,.2f}")
    print(f"   Conversions:  {df['conversions'].sum():>15,.1f}")
    print(f"   Conv. Value:  ${df['conversions_value'].sum():>14,.2f}")
    
    if df['clicks'].sum() > 0:
        ctr = (df['clicks'].sum() / df['impressions'].sum()) * 100
        cpc = df['cost'].sum() / df['clicks'].sum()
        print(f"   CTR:          {ctr:>15,.2f}%")
        print(f"   Avg CPC:      ${cpc:>14,.2f}")
    
    if df['conversions'].sum() > 0:
        cpa = df['cost'].sum() / df['conversions'].sum()
        print(f"   Avg CPA:      ${cpa:>14,.2f}")
    
    print(f"\n[CAMPAIGNS]")
    for i, campaign in enumerate(df['campaign_name'].unique(), 1):
        print(f"   {i}. {campaign}")
    
    print(f"\n[FILE LOCATION]")
    print(f"   {data_file.resolve()}")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/analyze_data.py <client-slug>")
        sys.exit(1)
    
    analyze_client_data(sys.argv[1])

