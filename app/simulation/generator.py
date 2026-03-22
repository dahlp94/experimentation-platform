from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any, Optional

import numpy as np
import pandas as pd

from app.simulation.config import SimulationConfig
from app.utils.seed import make_rng


def _seconds_between(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds()


def generate_users(cfg: SimulationConfig, rng: np.random.Generator) -> pd.DataFrame:
    n = cfg.population.n_users
    exp_start = cfg.experiment.start_ts
    countries = np.array(["US", "CA", "UK"])
    platforms = np.array(["web", "ios", "android"])
    age_buckets = np.array(["18-24", "25-34", "35-44", "45+"])
    channels = np.array(["organic", "ads", "referral", "email"])

    user_ids = np.arange(1, n + 1, dtype=np.int64)
    span_days = 365
    offsets = rng.integers(1, span_days + 1, size=n)
    signup_ts = np.array(
        [exp_start - timedelta(days=int(d)) for d in offsets], dtype=object
    )

    df = pd.DataFrame(
        {
            "user_id": user_ids,
            "signup_ts": signup_ts,
            "country": rng.choice(countries, size=n),
            "platform": rng.choice(platforms, size=n),
            "age_bucket": rng.choice(age_buckets, size=n),
            "acquisition_channel": rng.choice(channels, size=n),
            "is_premium": rng.random(size=n) < 0.12,
        }
    )
    df["created_at"] = datetime(2026, 1, 15, 12, 0, 0)
    return df


def generate_experiment(cfg: SimulationConfig) -> pd.DataFrame:
    e = cfg.experiment
    return pd.DataFrame(
        [
            {
                "experiment_id": e.experiment_id,
                "experiment_name": e.experiment_name,
                "status": e.status,
                "start_ts": e.start_ts,
                "end_ts": e.end_ts,
                "primary_metric": e.primary_metric,
                "randomization_unit": e.randomization_unit,
                "control_label": e.control_label,
                "treatment_label": e.treatment_label,
                "hypothesis_direction": e.hypothesis_direction,
                "created_at": datetime(2026, 1, 15, 12, 0, 0),
            }
        ]
    )


def generate_assignments(
    cfg: SimulationConfig, users: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    n = len(users)
    in_experiment = rng.random(n) < cfg.assignment.traffic_fraction
    user_ids = users.loc[in_experiment, "user_id"].to_numpy(dtype=np.int64)
    if len(user_ids) == 0:
        return pd.DataFrame(
            columns=[
                "experiment_id",
                "user_id",
                "variant",
                "assigned_ts",
                "assignment_channel",
                "is_eligible",
            ]
        )

    p_treat = cfg.assignment.treatment_probability
    is_treatment = rng.random(len(user_ids)) < p_treat
    control = cfg.experiment.control_label
    treatment = cfg.experiment.treatment_label
    variants = np.where(is_treatment, treatment, control)

    start = cfg.experiment.start_ts
    end = cfg.experiment.end_ts
    window_sec = max(_seconds_between(start, end), 1.0)
    frac = rng.uniform(0.0, min(7 * 86400 / window_sec, 1.0), size=len(user_ids))
    assigned_ts = np.array(
        [start + timedelta(seconds=float(f) * window_sec) for f in frac], dtype=object
    )

    return pd.DataFrame(
        {
            "experiment_id": cfg.experiment.experiment_id,
            "user_id": user_ids,
            "variant": variants,
            "assigned_ts": assigned_ts,
            "assignment_channel": "randomizer",
            "is_eligible": True,
        }
    )


def _conversion_prob(cfg: SimulationConfig, variant: str) -> float:
    if variant == cfg.experiment.control_label:
        return cfg.behavior.control_conversion_prob
    return cfg.behavior.treatment_conversion_prob


def _sorted_session_starts(
    assigned_ts: datetime,
    end_ts: datetime,
    n_sessions: int,
    rng: np.random.Generator,
) -> list[datetime]:
    sec = _seconds_between(assigned_ts, end_ts)
    if sec <= 0:
        return [assigned_ts]
    raw = np.sort(rng.uniform(0.0, sec, size=n_sessions))
    return [assigned_ts + timedelta(seconds=float(x)) for x in raw]


def generate_events(
    cfg: SimulationConfig,
    users: pd.DataFrame,
    assignments: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    eid = cfg.experiment.experiment_id
    end_ts = cfg.experiment.end_ts
    beh = cfg.behavior

    user_signup = users.set_index("user_id")["signup_ts"].to_dict()

    for _, row in assignments.iterrows():
        uid = int(row["user_id"])
        variant = str(row["variant"])
        assigned_ts = row["assigned_ts"]
        if not isinstance(assigned_ts, datetime):
            assigned_ts = pd.Timestamp(assigned_ts).to_pydatetime()

        p_conv = _conversion_prob(cfg, variant)
        converts = rng.random() < p_conv
        conv_session: Optional[int] = None
        if converts:
            n_sess_draw = max(1, int(rng.poisson(beh.mean_sessions_per_user)))
            conv_session = int(rng.integers(0, n_sess_draw))
        else:
            n_sess_draw = max(1, int(rng.poisson(beh.mean_sessions_per_user)))

        session_starts = _sorted_session_starts(assigned_ts, end_ts, n_sess_draw, rng)

        if beh.include_pre_period_events and rng.random() < 0.35:
            signup = user_signup[uid]
            if not isinstance(signup, datetime):
                signup = pd.Timestamp(signup).to_pydatetime()
            gap = _seconds_between(signup, assigned_ts)
            low, high = 3600.0, gap - 600.0
            if high > low:
                pre_t0 = signup + timedelta(seconds=float(rng.uniform(low, high)))
                if pre_t0 < assigned_ts:
                    pre_sess = f"pre_{uid}_{int(rng.integers(1, 1_000_000))}"
                    rows.append(
                        {
                            "user_id": uid,
                            "experiment_id": eid,
                            "event_ts": pre_t0,
                            "event_name": "session_start",
                            "session_id": pre_sess,
                            "event_value": np.nan,
                            "metadata_json": "{}",
                        }
                    )
                    rows.append(
                        {
                            "user_id": uid,
                            "experiment_id": eid,
                            "event_ts": pre_t0 + timedelta(seconds=int(rng.integers(5, 120))),
                            "event_name": "page_view",
                            "session_id": pre_sess,
                            "event_value": np.nan,
                            "metadata_json": json.dumps({"path": "/"}),
                        }
                    )

        conversion_emitted = False

        for s_idx, s_start in enumerate(session_starts):
            sess = f"sess_{uid}_{s_idx}_{int(rng.integers(1, 1_000_000))}"
            t = s_start
            rows.append(
                {
                    "user_id": uid,
                    "experiment_id": eid,
                    "event_ts": t,
                    "event_name": "session_start",
                    "session_id": sess,
                    "event_value": np.nan,
                    "metadata_json": "{}",
                }
            )
            n_pv = int(rng.integers(2, 8))
            for _ in range(n_pv):
                t = t + timedelta(seconds=int(rng.integers(3, 90)))
                rows.append(
                    {
                        "user_id": uid,
                        "experiment_id": eid,
                        "event_ts": t,
                        "event_name": "page_view",
                        "session_id": sess,
                        "event_value": np.nan,
                        "metadata_json": json.dumps({"path": "/product"}),
                    }
                )

            if rng.random() < beh.add_to_cart_prob:
                t = t + timedelta(seconds=int(rng.integers(5, 60)))
                rows.append(
                    {
                        "user_id": uid,
                        "experiment_id": eid,
                        "event_ts": t,
                        "event_name": "add_to_cart",
                        "session_id": sess,
                        "event_value": np.nan,
                        "metadata_json": "{}",
                    }
                )

            if converts and conv_session == s_idx and not conversion_emitted:
                t = t + timedelta(seconds=int(rng.integers(10, 120)))
                rows.append(
                    {
                        "user_id": uid,
                        "experiment_id": eid,
                        "event_ts": t,
                        "event_name": "conversion",
                        "session_id": sess,
                        "event_value": np.nan,
                        "metadata_json": "{}",
                    }
                )
                conversion_emitted = True
                amt = float(rng.normal(beh.purchase_amount_mean, beh.purchase_amount_std))
                amt = max(5.0, amt)
                t = t + timedelta(seconds=int(rng.integers(2, 30)))
                rows.append(
                    {
                        "user_id": uid,
                        "experiment_id": eid,
                        "event_ts": t,
                        "event_name": "purchase",
                        "session_id": sess,
                        "event_value": round(amt, 2),
                        "metadata_json": json.dumps({"sku": "demo"}),
                    }
                )

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.sort_values(["user_id", "event_ts", "event_name"]).reset_index(drop=True)
    return df


def run_simulation(cfg: SimulationConfig) -> dict[str, pd.DataFrame]:
    rng = make_rng(cfg.random_seed)
    users = generate_users(cfg, rng)
    experiment = generate_experiment(cfg)
    assignments = generate_assignments(cfg, users, rng)
    events = generate_events(cfg, users, assignments, rng)
    return {
        "users": users,
        "experiments": experiment,
        "assignments": assignments,
        "events": events,
    }
