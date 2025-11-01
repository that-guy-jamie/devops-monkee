#!/usr/bin/env python3
"""
init_all_clients.py - Pull 1 year of historical data for all configured clients

This script runs the 'init' command for all clients in the configs/clients directory.
It pulls exactly 1 year of historical campaign data for each client.

Usage:
    python scripts/init_all_clients.py [--parallel N] [--clients client1,client2,...]

Author: OneClickSEO PPC Management
Version: 0.1.0
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import time

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIGS_DIR = BASE_DIR / "configs" / "clients"


def run_init_for_client(slug: str) -> dict:
    """
    Run init command for a single client.
    
    Returns:
        dict with status, slug, and timing information
    """
    start_time = time.time()
    print(f"\n{'='*70}")
    print(f"[STARTING] {slug}")
    print(f"{'='*70}")
    
    try:
        # Find poetry executable
        import shutil
        poetry_path = shutil.which("poetry")
        if not poetry_path:
            # Try common Windows path
            poetry_path = r"C:\Users\james\AppData\Roaming\Python\Python313\Scripts\poetry.exe"
        
        # Run init command
        result = subprocess.run(
            [poetry_path, "run", "python", "ads_sync_cli.py", "init", slug],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per client
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            # Parse output for row count
            rows = 0
            for line in result.stdout.split('\n'):
                if 'After deduplication:' in line:
                    try:
                        rows = int(line.split(':')[1].strip().split()[0])
                    except:
                        pass
            
            print(f"[SUCCESS] {slug} - {rows:,} rows in {elapsed:.1f}s")
            return {
                'status': 'success',
                'slug': slug,
                'rows': rows,
                'elapsed': elapsed,
                'error': None
            }
        else:
            print(f"[FAILED] {slug}")
            if result.stderr:
                print(f"Stderr: {result.stderr}")
            if result.stdout:
                print(f"Stdout: {result.stdout[-500:]}")  # Last 500 chars
            error_msg = result.stderr or result.stdout or "Unknown error"
            return {
                'status': 'failed',
                'slug': slug,
                'rows': 0,
                'elapsed': elapsed,
                'error': error_msg[:200]  # First 200 chars of error
            }
    
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {slug} - exceeded 10 minutes")
        return {
            'status': 'timeout',
            'slug': slug,
            'rows': 0,
            'elapsed': 600,
            'error': 'Timeout after 10 minutes'
        }
    except Exception as e:
        print(f"[ERROR] {slug} - {str(e)}")
        return {
            'status': 'error',
            'slug': slug,
            'rows': 0,
            'elapsed': time.time() - start_time,
            'error': str(e)
        }


def main():
    parser = argparse.ArgumentParser(
        description='Pull 1 year of historical data for all clients'
    )
    parser.add_argument(
        '--clients',
        type=str,
        help='Comma-separated list of client slugs (default: all)'
    )
    parser.add_argument(
        '--skip',
        type=str,
        help='Comma-separated list of client slugs to skip'
    )
    
    args = parser.parse_args()
    
    # Get list of clients
    if args.clients:
        client_slugs = [s.strip() for s in args.clients.split(',')]
    else:
        # Auto-discover all client configs
        config_files = sorted(CONFIGS_DIR.glob("*.yaml"))
        client_slugs = [f.stem for f in config_files]
    
    # Apply skip list
    if args.skip:
        skip_list = [s.strip() for s in args.skip.split(',')]
        client_slugs = [s for s in client_slugs if s not in skip_list]
    
    print(f"\n{'='*70}")
    print(f"  INITIALIZING DATA PULL FOR {len(client_slugs)} CLIENTS")
    print(f"{'='*70}")
    print(f"\nPulling 1 year of historical campaign data...")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Track results
    results = []
    overall_start = time.time()
    
    # Process each client sequentially
    for i, slug in enumerate(client_slugs, 1):
        print(f"\n[{i}/{len(client_slugs)}] Processing: {slug}")
        result = run_init_for_client(slug)
        results.append(result)
    
    # Calculate summary
    overall_elapsed = time.time() - overall_start
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']
    errors = [r for r in results if r['status'] == 'error']
    timeouts = [r for r in results if r['status'] == 'timeout']
    
    total_rows = sum(r['rows'] for r in successful)
    avg_time = sum(r['elapsed'] for r in successful) / len(successful) if successful else 0
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"  EXECUTION SUMMARY")
    print(f"{'='*70}\n")
    print(f"Total Clients:     {len(client_slugs)}")
    print(f"Successful:        {len(successful)}")
    print(f"Failed:            {len(failed)}")
    print(f"Errors:            {len(errors)}")
    print(f"Timeouts:          {len(timeouts)}")
    print(f"\nTotal Rows:        {total_rows:,}")
    print(f"Avg Time/Client:   {avg_time:.1f}s")
    print(f"Total Time:        {overall_elapsed/60:.1f} minutes")
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show failures
    if failed or errors or timeouts:
        print(f"\n{'='*70}")
        print(f"  FAILURES")
        print(f"{'='*70}\n")
        for r in failed + errors + timeouts:
            print(f"{r['slug']}: {r['error']}")
    
    print(f"\n{'='*70}\n")
    
    # Exit code
    sys.exit(0 if len(successful) == len(client_slugs) else 1)


if __name__ == "__main__":
    main()

