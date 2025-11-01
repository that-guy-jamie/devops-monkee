#!/usr/bin/env python3
"""Check database constraints on aggregate tables."""

from backend.database import sync_engine
from sqlalchemy import text

def check_table_constraints(table_name):
    """Check constraints on a table."""
    query = f"""
    SELECT constraint_name, constraint_type
    FROM information_schema.table_constraints
    WHERE table_name = '{table_name}' AND constraint_type = 'UNIQUE'
    """

    with sync_engine.connect() as conn:
        result = conn.execute(text(query))
        constraints = result.fetchall()

        print(f"Unique constraints on {table_name}:")
        for constraint in constraints:
            print(f"  {constraint[0]}: {constraint[1]}")
        print()

        return constraints

def main():
    """Check constraints on aggregate tables."""
    tables = [
        "agg_campaign_daily",
        "agg_adgroup_daily",
        "agg_keyword_daily",
        "agg_search_term_daily"
    ]

    for table in tables:
        check_table_constraints(table)

if __name__ == "__main__":
    main()
