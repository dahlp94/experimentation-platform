from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass(frozen=True)
class UserRecord:
    user_id: int
    signup_ts: datetime
    country: str
    platform: str
    age_bucket: str
    acquisition_channel: str
    is_premium: bool


@dataclass(frozen=True)
class ExperimentRecord:
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
class AssignmentRecord:
    experiment_id: str
    user_id: int
    variant: str
    assigned_ts: datetime
    assignment_channel: str
    is_eligible: bool


@dataclass(frozen=True)
class EventRecord:
    user_id: int
    experiment_id: Optional[str]
    event_ts: datetime
    event_name: str
    session_id: Optional[str]
    event_value: Optional[float]
    metadata_json: dict[str, Any]
