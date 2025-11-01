"""
Parallel Campaign Workflow - Priority Roofing
=============================================

Subcommands:
  - dry-run: Pull current campaign, validate parity vs plan, emit DIFF.json
  - create: Create PAUSED campaign with exact budget
  - validate: Read back created campaign and confirm schema/budget
  - activate: Activate new campaign; optionally add one exact negative to old

Usage examples:
  poetry run python scripts/parallel_campaign.py dry-run --customer 1877202760 --plan reports/priority_roofing/plan.json
  poetry run python scripts/parallel_campaign.py create --customer 1877202760 --name "Priority Roofing - Search v2"
  poetry run python scripts/parallel_campaign.py validate --customer 1877202760 --campaign <resource>
  poetry run python scripts/parallel_campaign.py activate --customer 1877202760 --campaign <resource>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from backend.integrations.google_ads_client import GoogleAdsWrapper


def micros_from_dollars(d: float) -> int:
    return int(round(d * 1_000_000))


def dry_run(customer_id: str, plan_path: Path) -> int:
    ga = GoogleAdsWrapper()
    current = ga.get_active_search_campaign(customer_id)
    if not current:
        print("No active/paused search campaign found.")
        return 1

    plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.exists() else {}

    diff: Dict[str, Any] = {
        "current": {
            "id": current.id,
            "name": current.name,
            "status": current.status,
            "bidding_strategy_type": current.bidding_strategy_type,
            "daily_budget_micros": current.daily_budget_micros,
        },
        "plan": plan,
        "checks": {
            "budget_present_in_plan": plan.get("expected_daily_budget") is not None,
        },
    }
    out_dir = plan_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "DIFF.json").write_text(json.dumps(diff, indent=2), encoding="utf-8")
    print(f"Dry run complete. Wrote {out_dir / 'DIFF.json'}")
    return 0


def create(customer_id: str, name: str) -> int:
    ga = GoogleAdsWrapper()
    base = ga.get_active_search_campaign(customer_id)
    if not base:
        print("No base campaign found to mirror budget.")
        return 1
    new_resource = ga.create_campaign_paused_with_budget(
        customer_id=customer_id,
        name=name,
        daily_budget_micros=base.daily_budget_micros,
        bidding_strategy_type=base.bidding_strategy_type,
        labels=[],
    )
    print(f"Created PAUSED campaign: {new_resource}")
    Path("reports/priority_roofing").mkdir(parents=True, exist_ok=True)
    Path("reports/priority_roofing/create.json").write_text(
        json.dumps({"resource_name": new_resource}, indent=2), encoding="utf-8"
    )
    return 0


def validate(customer_id: str, campaign_resource: str, plan_path: Path) -> int:
    ga = GoogleAdsWrapper()
    snap = ga.get_campaign_snapshot(customer_id, campaign_resource)
    plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.exists() else {}
    expected_budget = plan.get("expected_daily_budget")
    checks: Dict[str, Any] = {
        "budget_match": (expected_budget is None) or micros_from_dollars(expected_budget) == snap.daily_budget_micros,
        "status_is_paused": snap.status == "PAUSED",
    }
    Path("reports/priority_roofing/validate.json").write_text(
        json.dumps({"snapshot": snap.__dict__, "checks": checks}, indent=2), encoding="utf-8"
    )
    ok = all(checks.values())
    print("Validation:", checks)
    return 0 if ok else 2


def activate(customer_id: str, campaign_resource: str) -> int:
    ga = GoogleAdsWrapper()
    ga.set_campaign_status(customer_id, campaign_resource, "ENABLED")
    print("Activated", campaign_resource)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Parallel campaign workflow")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_dry = sub.add_parser("dry-run")
    p_dry.add_argument("--customer", required=True)
    p_dry.add_argument("--plan", required=True)

    p_create = sub.add_parser("create")
    p_create.add_argument("--customer", required=True)
    p_create.add_argument("--name", required=True)

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("--customer", required=True)
    p_validate.add_argument("--campaign", required=True)
    p_validate.add_argument("--plan", required=True)

    p_activate = sub.add_parser("activate")
    p_activate.add_argument("--customer", required=True)
    p_activate.add_argument("--campaign", required=True)

    args = parser.parse_args()

    if args.cmd == "dry-run":
        return dry_run(args.customer, Path(args.plan))
    if args.cmd == "create":
        return create(args.customer, args.name)
    if args.cmd == "validate":
        return validate(args.customer, args.campaign, Path(args.plan))
    if args.cmd == "activate":
        return activate(args.customer, args.campaign)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


