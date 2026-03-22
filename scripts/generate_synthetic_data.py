#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.simulation.config import load_simulation_config
from app.simulation.export import export_dataframes
from app.simulation.generator import run_simulation
from app.utils.paths import repo_root, synthetic_data_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic CSVs under data/synthetic/")
    parser.add_argument(
        "--config",
        type=Path,
        default=repo_root() / "configs" / "simulation_config.yaml",
        help="Path to simulation YAML config",
    )
    args = parser.parse_args()
    cfg = load_simulation_config(args.config)
    frames = run_simulation(cfg)
    out = synthetic_data_dir()
    export_dataframes(out, frames)
    print("Wrote CSVs to", out)


if __name__ == "__main__":
    main()
