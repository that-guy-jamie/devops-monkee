#!/usr/bin/env python3
"""
Auto-discover and run audits for all configured clients.
"""
import requests
import time
import sys
from pathlib import Path
from typing import List, Dict

API_URL = "http://localhost:8000"
CLIENTS_DIR = Path("../ads_sync/configs/clients")

def discover_clients() -> List[str]:
    """Discover all client slugs from config files."""
    if not CLIENTS_DIR.exists():
        print(f"❌ Clients directory not found: {CLIENTS_DIR}")
        sys.exit(1)
    
    client_files = list(CLIENTS_DIR.glob("*.yaml"))
    slugs = [f.stem for f in client_files]
    
    print(f"✓ Discovered {len(slugs)} client(s): {', '.join(slugs)}\n")
    return slugs

def queue_job(slug: str, command: str) -> str:
    """Queue a job for a client."""
    try:
        response = requests.post(
            f"{API_URL}/api/runbooks/execute",
            json={"slug": slug, "command": command},
            timeout=10
        )
        response.raise_for_status()
        job_id = response.json()["job_id"]
        print(f"  ✓ Job queued: {job_id}")
        return job_id
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return None

def get_job_status(job_id: str) -> Dict:
    """Get job status."""
    try:
        response = requests.get(f"{API_URL}/api/jobs/{job_id}/status", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}

def main():
    print("\n🚀 RUNNING AUDITS FOR ALL CLIENTS\n" + "="*60 + "\n")
    
    # Discover clients
    slugs = discover_clients()
    
    if not slugs:
        print("❌ No clients found")
        sys.exit(1)
    
    # Queue all jobs
    print("📤 Queuing jobs...\n")
    jobs = []
    for slug in slugs:
        print(f"Queuing: {slug}")
        job_id = queue_job(slug, "validate")
        if job_id:
            jobs.append({"slug": slug, "job_id": job_id})
        print()
    
    # Wait for completion
    print("⏳ Waiting for jobs to complete...\n")
    time.sleep(5)
    
    # Check all job statuses
    print("📊 JOB RESULTS\n" + "="*60 + "\n")
    
    completed = 0
    failed = 0
    
    for job in jobs:
        status = get_job_status(job["job_id"])
        
        print(f"📌 Client: {job['slug']}")
        print(f"   Job ID: {job['job_id']}")
        print(f"   Status: {status['status']}")
        
        if status["status"] == "finished":
            completed += 1
            print("   ✓ Audit complete")
            
            # Show key findings
            result = status.get("result", "")
            if "[OK] Config file valid" in result:
                print("   ✓ Config valid")
            if "[MISSING] Master CSV" in result:
                print("   ⚠  No existing data (ready for init)")
        elif status["status"] == "failed":
            failed += 1
            print(f"   ❌ Error: {status.get('error', 'Unknown error')}")
        
        print()
    
    # Summary
    print("="*60)
    print("📈 SUMMARY")
    print("="*60)
    print(f"Total Clients:    {len(jobs)}")
    print(f"Completed:        {completed}")
    print(f"Failed:           {failed}")
    print("="*60)
    
    if completed == len(jobs):
        print("\n🎉 ALL AUDITS COMPLETED SUCCESSFULLY!\n")
    else:
        print("\n⚠  Some audits did not complete. Review errors above.\n")

if __name__ == "__main__":
    main()

