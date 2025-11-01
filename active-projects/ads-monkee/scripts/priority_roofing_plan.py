"""
Priority Roofing Campaign Plan Builder
======================================

Reads analysis outputs from Output/priorityroofers.com and produces a
normalized campaign plan JSON for parallel campaign creation.

Usage:
    poetry run python scripts/priority_roofing_plan.py \
        --source "C:/Users/james/Desktop/Projects/Output/priorityroofers.com" \
        --out "reports/priority_roofing/plan.json"
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


def read_csv_safe(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def dataframe_to_list(df: pd.DataFrame) -> List[Dict[str, Any]]:
    if df.empty:
        return []
    return json.loads(df.to_json(orient="records"))


def build_plan(source_dir: Path) -> Dict[str, Any]:
    adds_path = source_dir / "pr-roofing_editor_keywords_to_add.csv"
    negs_path = source_dir / "pr-roofing_editor_negative_keywords.csv"
    exact_candidates_path = source_dir / "pr-roofing_exact_terms_candidates.csv"
    neg_candidates_path = source_dir / "pr-roofing_negative_terms_candidates.csv"

    adds_df = read_csv_safe(adds_path)
    negs_df = read_csv_safe(negs_path)
    exact_df = read_csv_safe(exact_candidates_path)
    negcand_df = read_csv_safe(neg_candidates_path)

    plan: Dict[str, Any] = {
        "client": "Priority Roofing",
        "created_from": str(source_dir),
        "expected_daily_budget": None,  # Filled during validation via Google Ads API
        "ad_groups": [],
        "keywords_to_add": dataframe_to_list(adds_df),
        "negative_keywords": dataframe_to_list(negs_df),
        "exact_terms_candidates": dataframe_to_list(exact_df),
        "negative_terms_candidates": dataframe_to_list(negcand_df),
        "notes": [
            "Budget must match original campaign.",
            "Create new campaign in PAUSED state, validate schema, then activate and pause old.",
        ],
    }

    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Priority Roofing campaign plan JSON")
    parser.add_argument("--source", required=True, help="Path to Output/priorityroofers.com directory")
    parser.add_argument("--out", required=True, help="Output path for plan.json (inside project)")

    args = parser.parse_args()

    source_dir = Path(args.source)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    plan = build_plan(source_dir)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)

    print(f"Wrote plan to {out_path}")


if __name__ == "__main__":
    main()


