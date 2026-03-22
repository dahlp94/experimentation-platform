from __future__ import annotations

import pandas as pd

def test_event_users_exist(simulation_frames: dict) -> None:
    out = simulation_frames
    u = set(out["users"]["user_id"].tolist())
    e = set(out["events"]["user_id"].tolist())
    assert e <= u


def test_event_experiment_ids_exist(simulation_frames: dict) -> None:
    out = simulation_frames
    exp_ids = set(out["experiments"]["experiment_id"].tolist())
    for eid in out["events"]["experiment_id"].dropna().unique():
        assert eid in exp_ids


def test_post_assignment_funnel_events_not_before_assignment(
    simulation_frames: dict,
) -> None:
    out = simulation_frames
    post_only = {"add_to_cart", "conversion", "purchase"}
    m = out["events"].merge(
        out["assignments"],
        on=["user_id", "experiment_id"],
        how="left",
        suffixes=("", "_asg"),
    )
    m["event_ts"] = pd.to_datetime(m["event_ts"])
    m["assigned_ts"] = pd.to_datetime(m["assigned_ts"])
    bad = m[m["event_name"].isin(post_only) & (m["event_ts"] < m["assigned_ts"])]
    assert len(bad) == 0


def test_pre_period_events_after_signup(simulation_frames: dict) -> None:
    out = simulation_frames
    users = out["users"].copy()
    users["signup_ts"] = pd.to_datetime(users["signup_ts"])
    m = out["events"].merge(users[["user_id", "signup_ts"]], on="user_id", how="left")
    m["event_ts"] = pd.to_datetime(m["event_ts"])
    assert (m["event_ts"] >= m["signup_ts"]).all()


def test_purchase_positive_value(simulation_frames: dict) -> None:
    out = simulation_frames
    pur = out["events"][out["events"]["event_name"] == "purchase"]
    assert (pur["event_value"] > 0).all()


def test_non_purchase_event_values_null_or_zero(simulation_frames: dict) -> None:
    out = simulation_frames
    sub = out["events"][out["events"]["event_name"] != "purchase"]
    vals = sub["event_value"]
    mask = vals.notna()
    assert (vals[mask] == 0).all() or (vals[mask].abs() < 1e-9).all()
    # generator uses NaN for non-purchase; allow no non-null non-zero
    assert not ((mask) & (vals != 0)).any()


def test_at_most_one_conversion_per_user(simulation_frames: dict) -> None:
    out = simulation_frames
    c = out["events"][out["events"]["event_name"] == "conversion"]
    counts = c.groupby("user_id").size()
    assert (counts <= 1).all()
