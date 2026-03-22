#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db.connection import get_engine


def main() -> None:
    engine = get_engine()

    with engine.connect() as conn:
        n_users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar_one()
        n_exp = conn.execute(text("SELECT COUNT(*) FROM experiments")).scalar_one()
        n_asg = conn.execute(text("SELECT COUNT(*) FROM assignments")).scalar_one()
        n_evt = conn.execute(text("SELECT COUNT(*) FROM events")).scalar_one()

        dup_q = text(
            """
            SELECT COUNT(*) FROM (
                SELECT experiment_id, user_id, COUNT(*) AS c
                FROM assignments
                GROUP BY experiment_id, user_id
                HAVING COUNT(*) > 1
            ) t
            """
        )
        n_dup = conn.execute(dup_q).scalar_one()

        split = pd.read_sql(
            text(
                "SELECT variant, COUNT(*) AS n FROM assignments GROUP BY variant ORDER BY variant"
            ),
            conn,
        )

        evt_types = pd.read_sql(
            text(
                "SELECT event_name, COUNT(*) AS n FROM events GROUP BY event_name ORDER BY event_name"
            ),
            conn,
        )

        ts_bounds = pd.read_sql(
            text(
                "SELECT MIN(event_ts) AS min_ts, MAX(event_ts) AS max_ts FROM events"
            ),
            conn,
        )

        conv_users = pd.read_sql(
            text(
                """
                SELECT COUNT(DISTINCT user_id) AS converting_users
                FROM events
                WHERE event_name = 'conversion'
                """
            ),
            conn,
        )

    pct_conv = (
        100.0 * float(conv_users["converting_users"].iloc[0]) / float(n_asg)
        if n_asg
        else 0.0
    )

    print("=== Seed data verification ===")
    print(f"users:              {n_users}")
    print(f"experiments:        {n_exp}")
    print(f"assignments:        {n_asg}")
    print(f"events:             {n_evt}")
    print(f"duplicate (exp,user) rows: {n_dup}")
    print("\nAssignment split:")
    print(split.to_string(index=False))
    print("\nEvent types:")
    print(evt_types.to_string(index=False))
    print("\nEvent timestamps:")
    print(ts_bounds.to_string(index=False))
    print(f"\nUsers with conversion event: {int(conv_users['converting_users'].iloc[0])}")
    print(f"Percent of assigned users converting: {pct_conv:.2f}%")


if __name__ == "__main__":
    main()
