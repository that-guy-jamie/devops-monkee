#!/usr/bin/env python3
"""Check the constraint definition for agg_keyword_daily table."""

from backend.database import sync_engine
from sqlalchemy import text

def check_keyword_constraint():
    """Check the constraint definition for agg_keyword_daily."""
    query = """
    SELECT
        tc.constraint_name,
        tc.constraint_type,
        kcu.column_name,
        kcu.ordinal_position
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_name = kcu.table_name
    WHERE tc.table_name = 'agg_keyword_daily'
        AND tc.constraint_type = 'UNIQUE'
    ORDER BY tc.constraint_name, kcu.ordinal_position
    """

    with sync_engine.connect() as conn:
        result = conn.execute(text(query))
        constraints = result.fetchall()

        print("Constraint details for agg_keyword_daily:")
        current_constraint = None
        for row in constraints:
            constraint_name, constraint_type, column_name, ordinal_position = row
            if constraint_name != current_constraint:
                if current_constraint:
                    print()
                print(f"  {constraint_name}:")
                current_constraint = constraint_name
            print(f"    {ordinal_position}. {column_name}")

if __name__ == "__main__":
    check_keyword_constraint()
