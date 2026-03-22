#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db.connection import get_engine
from app.db.ddl_runner import run_schema_ddl
from app.utils.paths import schema_dir


def main() -> None:
    engine = get_engine()
    run_schema_ddl(engine, schema_dir())
    print("Schema applied from", schema_dir())


if __name__ == "__main__":
    main()
