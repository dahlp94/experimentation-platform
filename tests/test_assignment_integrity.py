from __future__ import annotations

import pandas as pd

from app.simulation.config import SimulationConfig


def test_at_most_one_assignment_per_user_per_experiment(simulation_frames: dict) -> None:
    out = simulation_frames
    g = out["assignments"].groupby(["experiment_id", "user_id"]).size()
    assert (g <= 1).all()


def test_only_allowed_variants(
    simulation_config: SimulationConfig, simulation_frames: dict
) -> None:
    out = simulation_frames
    cfg = simulation_config
    allowed = {cfg.experiment.control_label, cfg.experiment.treatment_label}
    assert set(out["assignments"]["variant"].unique()) <= allowed


def test_treatment_split_near_config(
    simulation_config: SimulationConfig, simulation_frames: dict
) -> None:
    out = simulation_frames
    cfg = simulation_config
    vc = out["assignments"]["variant"].value_counts(normalize=True)
    p = cfg.assignment.treatment_probability
    treat_label = cfg.experiment.treatment_label
    assert abs(float(vc.get(treat_label, 0.0)) - p) < 0.02


def test_assignment_timestamps_within_experiment_window(
    simulation_config: SimulationConfig, simulation_frames: dict
) -> None:
    out = simulation_frames
    cfg = simulation_config
    start, end = cfg.experiment.start_ts, cfg.experiment.end_ts
    ts = pd.to_datetime(out["assignments"]["assigned_ts"])
    assert (ts >= pd.Timestamp(start)).all()
    assert (ts <= pd.Timestamp(end)).all()


def test_assigned_users_exist_in_users(simulation_frames: dict) -> None:
    out = simulation_frames
    u = set(out["users"]["user_id"].tolist())
    a = set(out["assignments"]["user_id"].tolist())
    assert a <= u
