from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ExperimentConfig:
    experiment_id: str
    experiment_name: str
    status: str
    start_ts: datetime
    end_ts: datetime
    primary_metric: str
    randomization_unit: str
    control_label: str
    treatment_label: str
    hypothesis_direction: str


@dataclass(frozen=True)
class PopulationConfig:
    n_users: int


@dataclass(frozen=True)
class AssignmentConfig:
    traffic_fraction: float
    treatment_probability: float


@dataclass(frozen=True)
class BehaviorConfig:
    mean_sessions_per_user: float
    control_conversion_prob: float
    treatment_conversion_prob: float
    add_to_cart_prob: float
    purchase_amount_mean: float
    purchase_amount_std: float
    include_pre_period_events: bool


@dataclass(frozen=True)
class SimulationConfig:
    random_seed: int
    experiment: ExperimentConfig
    population: PopulationConfig
    assignment: AssignmentConfig
    behavior: BehaviorConfig


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


def load_simulation_config(path: Path) -> SimulationConfig:
    raw: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    exp = raw["experiment"]
    experiment = ExperimentConfig(
        experiment_id=exp["experiment_id"],
        experiment_name=exp["experiment_name"],
        status=exp["status"],
        start_ts=_parse_ts(exp["start_ts"]),
        end_ts=_parse_ts(exp["end_ts"]),
        primary_metric=exp["primary_metric"],
        randomization_unit=exp["randomization_unit"],
        control_label=exp["control_label"],
        treatment_label=exp["treatment_label"],
        hypothesis_direction=exp["hypothesis_direction"],
    )
    pop = raw["population"]
    population = PopulationConfig(n_users=int(pop["n_users"]))
    asn = raw["assignment"]
    assignment = AssignmentConfig(
        traffic_fraction=float(asn["traffic_fraction"]),
        treatment_probability=float(asn["treatment_probability"]),
    )
    beh = raw["behavior"]
    behavior = BehaviorConfig(
        mean_sessions_per_user=float(beh["mean_sessions_per_user"]),
        control_conversion_prob=float(beh["control_conversion_prob"]),
        treatment_conversion_prob=float(beh["treatment_conversion_prob"]),
        add_to_cart_prob=float(beh["add_to_cart_prob"]),
        purchase_amount_mean=float(beh["purchase_amount_mean"]),
        purchase_amount_std=float(beh["purchase_amount_std"]),
        include_pre_period_events=bool(beh["include_pre_period_events"]),
    )
    return SimulationConfig(
        random_seed=int(raw["random_seed"]),
        experiment=experiment,
        population=population,
        assignment=assignment,
        behavior=behavior,
    )
