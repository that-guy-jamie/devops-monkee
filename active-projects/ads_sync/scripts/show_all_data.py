#!/usr/bin/env python3
"""
Show summary of all downloaded client data.
"""
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def main():
    results = []
    total_rows = 0
    
    print('\n' + '='*100)
    print('  PHASE 1 COMPLETE - ALL CLIENT DATA SUMMARY')
    print('='*100 + '\n')
    
    for client_dir in sorted(DATA_DIR.glob('*')):
        if not client_dir.is_dir():
            continue
            
        csv_file = client_dir / f'{client_dir.name}-master-campaign_data.csv'
        
        if csv_file.exists():
            try:
                df = pd.read_csv(csv_file)
                rows = len(df)
                total_rows += rows
                
                results.append({
                    'Client': client_dir.name,
                    'Rows': rows
                })
                
                print(f'{client_dir.name:<50} {rows:>8,} rows')
            except Exception as e:
                print(f'{client_dir.name:<50} [ERROR: {str(e)[:30]}]')
    
    print('\n' + '='*100)
    print(f'TOTAL: {len(results)} clients with {total_rows:,} rows of campaign data')
    print('='*100 + '\n')
    
    # Show top 10 by data volume
    results_sorted = sorted(results, key=lambda x: x['Rows'], reverse=True)
    print('\nTOP 10 CLIENTS BY DATA VOLUME:')
    print('-'*60)
    for i, r in enumerate(results_sorted[:10], 1):
        print(f'{i:2}. {r["Client"]:<45} {r["Rows"]:>8,} rows')
    print()

if __name__ == "__main__":
    main()

