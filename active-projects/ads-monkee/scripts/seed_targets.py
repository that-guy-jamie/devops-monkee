"""
Seed Client Targets
====================

Seeds the client_targets table with performance goals for each client.

Usage:
    poetry run python scripts/seed_targets.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import get_sync_db
from backend.models import Client, ClientTargets


def seed_targets():
    """Seed client targets."""
    print("[SEED TARGETS] Starting...")
    
    with get_sync_db() as db:
        # Get all clients
        clients = db.query(Client).all()
        
        if not clients:
            print("[SEED TARGETS] No clients found. Run seed_clients.py first.")
            return
        
        print(f"[SEED TARGETS] Found {len(clients)} clients")
        
        for client in clients:
            # Check if targets already exist
            existing = db.query(ClientTargets).filter(
                ClientTargets.client_id == client.id
            ).first()
            
            if existing:
                print(f"[SEED TARGETS] Targets already exist for {client.name}, skipping")
                continue
            
            # Create default targets
            # These should be customized per client in production
            targets = ClientTargets(
                client_id=client.id,
                target_cpa=50.00,  # $50 target CPA
                target_roas=4.0,   # 4:1 ROAS target
                monthly_budget=5000.00,  # $5k/month
                daily_budget_limit=200.00,  # $200/day
                cpa_alert_threshold_pct=1.3,  # Alert if CPA > target * 1.3
                roas_alert_threshold_pct=0.7,  # Alert if ROAS < target * 0.7
            )
            
            db.add(targets)
            print(f"[SEED TARGETS] Created targets for {client.name}")
            print(f"                Target CPA: ${targets.target_cpa}")
            print(f"                Target ROAS: {targets.target_roas}:1")
            print(f"                Monthly Budget: ${targets.monthly_budget}")
        
        db.commit()
        print()
        print("[SEED TARGETS] Complete!")


if __name__ == "__main__":
    seed_targets()

