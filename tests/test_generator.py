from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.simulation.config import SimulationConfig, load_simulation_config
from app.simulation.export import export_dataframes
from app.simulation.generator import run_simulation
from app.utils.paths import repo_root


def _config_path() -> Path:
    return repo_root() / "configs" / "simulation_config.yaml"


def test_generator_non_empty(
    simulation_config: SimulationConfig, simulation_frames: dict
) -> None:
    cfg = simulation_config
    out = simulation_frames
    assert len(out["users"]) == cfg.population.n_users
    assert len(out["experiments"]) == 1
    assert len(out["assignments"]) > 0
    assert len(out["events"]) > 0


def test_required_columns(simulation_frames: dict) -> None:
    out = simulation_frames
    assert set(out["users"].columns) >= {
        "user_id",
        "signup_ts",
        "country",
        "platform",
        "age_bucket",
        "acquisition_channel",
        "is_premium",
        "created_at",
    }
    assert set(out["experiments"].columns) >= {
        "experiment_id",
        "experiment_name",
        "status",
        "start_ts",
        "end_ts",
        "primary_metric",
        "randomization_unit",
        "control_label",
        "treatment_label",
        "hypothesis_direction",
        "created_at",
    }
    assert set(out["assignments"].columns) >= {
        "experiment_id",
        "user_id",
        "variant",
        "assigned_ts",
        "assignment_channel",
        "is_eligible",
    }
    assert set(out["events"].columns) >= {
        "user_id",
        "experiment_id",
        "event_ts",
        "event_name",
        "session_id",
        "event_value",
        "metadata_json",
    }


def test_experiment_single_row(
    simulation_config: SimulationConfig, simulation_frames: dict
) -> None:
    cfg = simulation_config
    out = simulation_frames
    assert len(out["experiments"]) == 1
    assert out["experiments"].iloc[0]["experiment_id"] == cfg.experiment.experiment_id


def test_reproducible_with_fixed_seed(tmp_path: Path) -> None:
    cfg = load_simulation_config(_config_path())
    a = run_simulation(cfg)
    b = run_simulation(cfg)
    pd.testing.assert_frame_equal(a["users"], b["users"])
    pd.testing.assert_frame_equal(a["experiments"], b["experiments"])
    pd.testing.assert_frame_equal(a["assignments"], b["assignments"])
    pd.testing.assert_frame_equal(a["events"], b["events"])

    export_dataframes(tmp_path, a)
    export_dataframes(tmp_path / "second", b)
    for name in ("users", "experiments", "assignments", "events"):
        p1 = tmp_path / f"{name}.csv"
        p2 = tmp_path / "second" / f"{name}.csv"
        assert p1.read_text() == p2.read_text()


def test_aggregate_summary_stable() -> None:
    cfg = load_simulation_config(_config_path())
    a = run_simulation(cfg)
    b = run_simulation(cfg)
    assert int(a["events"]["event_name"].value_counts().sum()) == int(
        b["events"]["event_name"].value_counts().sum()
    )
    assert a["events"]["event_name"].value_counts().to_dict() == b["events"][
        "event_name"
    ].value_counts().to_dict()
    assert int(a["assignments"]["variant"].value_counts().sum()) == int(
        b["assignments"]["variant"].value_counts().sum()
    )
