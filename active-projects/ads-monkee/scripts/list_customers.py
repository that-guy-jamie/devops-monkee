import argparse
import json
import sys
from pathlib import Path

# Ensure project root on path for integrations
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.integrations.google_ads_client import GoogleAdsIntegration


def list_customers(name_filter: str | None = None) -> list[dict]:
    gai = GoogleAdsIntegration()

    # Get list of accessible customer resource names from MCC
    customer_service = gai.get_service("CustomerService")
    accessible = customer_service.list_accessible_customers()
    resource_names = list(accessible.resource_names)

    results: list[dict] = []
    if not resource_names:
        return results

    ga_service = gai.get_service("GoogleAdsService")

    for rn in resource_names:
        customer_id = rn.split("/")[-1]
        query = (
            "SELECT customer.id, customer.descriptive_name, customer.time_zone, "
            "customer.currency_code, customer.manager FROM customer LIMIT 1"
        )
        try:
            response = ga_service.search(customer_id=customer_id, query=query)
            for row in response:
                entry = {
                    "id": str(row.customer.id),
                    "descriptive_name": row.customer.descriptive_name,
                    "time_zone": row.customer.time_zone,
                    "currency_code": row.customer.currency_code,
                    "manager": bool(row.customer.manager),
                    "resource_name": rn,
                }
                if name_filter:
                    if name_filter.lower() in (entry["descriptive_name"] or "").lower():
                        results.append(entry)
                else:
                    results.append(entry)
        except Exception as e:  # noqa: BLE001
            # Continue mapping others even if one fails
            results.append({
                "id": customer_id,
                "error": str(e),
                "resource_name": rn,
            })

    # Sort by name then id for readability
    results.sort(key=lambda x: (x.get("descriptive_name") or "", x.get("id") or ""))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="List accessible Google Ads customers with names"
    )
    parser.add_argument("--filter", help="Substring to filter by name", default=None)
    parser.add_argument(
        "--json-out",
        help="Optional path to write JSON output",
        type=Path,
        default=None,
    )
    args = parser.parse_args()

    rows = list_customers(args.filter)

    # Pretty print to stdout
    for r in rows:
        if "error" in r:
            print(f"- {r['id']}: ERROR {r['error']}")
        else:
            print(
                f"- {r['id']}: {r['descriptive_name']}  tz={r['time_zone']}  cur={r['currency_code']}  mgr={r['manager']}"
            )

    # Optional JSON dump
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()




