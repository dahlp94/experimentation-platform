from pathlib import Path

import pandas as pd


def export_dataframes(output_dir: Path, frames: dict[str, pd.DataFrame]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    frames["users"].to_csv(output_dir / "users.csv", index=False)
    frames["experiments"].to_csv(output_dir / "experiments.csv", index=False)
    frames["assignments"].to_csv(output_dir / "assignments.csv", index=False)
    frames["events"].to_csv(output_dir / "events.csv", index=False)
