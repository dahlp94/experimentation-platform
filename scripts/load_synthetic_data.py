#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db.connection import get_engine
from app.utils.paths import synthetic_data_dir


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["signup_ts", "created_at"], low_memory=False)


def _read_experiments(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["start_ts", "end_ts", "created_at"], low_memory=False)


def _read_assignments(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["assigned_ts"], low_memory=False)


def _read_events(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["event_ts"], low_memory=False)
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Load synthetic CSVs into PostgreSQL")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Directory containing users.csv, experiments.csv, assignments.csv, events.csv",
    )
    args = parser.parse_args()
    data_dir = args.data_dir or synthetic_data_dir()
    engine = get_engine()

    users = _read_csv(data_dir / "users.csv")
    experiments = _read_experiments(data_dir / "experiments.csv")
    assignments = _read_assignments(data_dir / "assignments.csv")
    events = _read_events(data_dir / "events.csv")

    with engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE TABLE events, assignments, experiments, users "
                "RESTART IDENTITY CASCADE"
            )
        )

    # Load order: users, experiments, assignments, events
    users.to_sql("users", engine, if_exists="append", index=False, chunksize=2000)
    experiments.to_sql("experiments", engine, if_exists="append", index=False)
    assignments.to_sql("assignments", engine, if_exists="append", index=False, chunksize=2000)
    events.to_sql("events", engine, if_exists="append", index=False, chunksize=5000)

    print("Loaded tables from", data_dir)


if __name__ == "__main__":
    main()
