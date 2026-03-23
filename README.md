# Experimentation Platform

This repository contains a production-style experimentation platform focused on correct assignment, raw behavioral event logging, and reproducible synthetic data generation. Week 1 establishes the data foundation for the project: a PostgreSQL schema, a config-driven simulator, CSV export, bulk load scripts, data verification, and automated integrity tests.

## Week 1 Summary

Week 1 completed the relational and simulation backbone of the project.

- **Schema:** four core tables (`users`, `experiments`, `assignments`, `events`) with indexes and a unique constraint on `(experiment_id, user_id)` in `assignments`.
- **Synthetic pipeline:** YAML-driven configuration, seeded random number generation, and CSV export under `data/synthetic/`.
- **Database workflow:** scripts to apply schema DDL, load CSVs in dependency order, and verify loaded data with quick sanity checks.
- **Validation:** pytest coverage for generator outputs, assignment rules, and event integrity.
- **Event-window enforcement:** experiment-period events are constrained to occur within the configured experiment window.

## Data Model

| Table | Role |
| ----- | ---- |
| **users** | Stable user dimensions such as signup time, country, platform, segment, and premium flag. |
| **experiments** | Metadata for each experiment, including start/end window, metric, labels, and randomization unit. |
| **assignments** | Which variant each user received and when; one row per user per experiment. |
| **events** | Timestamped raw behavioral logs such as `session_start`, `page_view`, `add_to_cart`, `conversion`, `purchase`, and optional pre-period activity. |

`event_value` stores numeric payloads when relevant, such as purchase amount. `metadata_json` stores small structured context as JSON.

## Why This Design Is Correct

- **Assignment and behavior are separated:** exposure is recorded once in `assignments`, while user response is recorded in `events`. This avoids mixing experimental design and outcomes in a single flat table.
- **User-level randomization is enforced:** the unique constraint on `(experiment_id, user_id)` guarantees one assignment per user per experiment, matching the configured randomization unit.
- **Events are stored as raw logs:** the data resembles production event streams and can later support SQL metric construction and statistical inference without re-simulating behavior.
- **Reproducibility is built in:** the `random_seed` in `configs/simulation_config.yaml` and centralized RNG setup make the pipeline deterministic for testing and demos.
- **Experiment-period integrity is enforced:** post-assignment events are generated within the experiment window, which keeps downstream metric computation clean and well-defined.

## How to Run

Prerequisites: Python 3.11+, PostgreSQL, and a valid `DATABASE_URL`.

1. **Environment**

   ```bash
   cp .env.example .env
   # Set DATABASE_URL in .env
   # Example: postgresql://user:pass@localhost:5432/exp_platform

   python -m venv venv_exp_platform
   source venv_exp_platform/bin/activate
   pip install -r requirements.txt
````

2. **Create schema**

   ```bash
   python scripts/create_schema.py
   ```

3. **Generate synthetic CSVs**

   ```bash
   python scripts/generate_synthetic_data.py
   ```

4. **Load into PostgreSQL**

   ```bash
   python scripts/load_synthetic_data.py
   ```

5. **Verify loaded data**

   ```bash
   python scripts/verify_seed_data.py
   ```

6. **Run tests**

   ```bash
   pytest tests/
   ```

The load script truncates `events`, `assignments`, `experiments`, and `users` in dependency-safe order before reloading, so repeated runs start from a clean state.

## Week 1 Integrity Guarantees

* one assignment per `(experiment_id, user_id)`
* assignment and behavior are stored separately
* experiment-period events occur within the configured experiment window
* optional pre-period events occur before assignment
* generated data is reproducible through a fixed random seed

## Simulation Logic

1. Generate `n_users` with categorical attributes and signup timestamps before the experiment window.
2. Create one experiment row from configuration.
3. Assign users into the experiment according to `traffic_fraction` and `treatment_probability`; assignment timestamps occur inside the configured assignment window.
4. For each assigned user, draw a session count from a Poisson distribution with a minimum of one session.
5. Place session starts between assignment time and experiment end.
6. Emit event logs for session activity and funnel behavior:

   * `session_start`
   * `page_view`
   * optional `add_to_cart`
   * optional `conversion`
   * `purchase` with positive `event_value` after conversion
7. Optionally emit pre-period `session_start` and `page_view` events after signup and before assignment.

Behavioral parameters can be tuned in `configs/simulation_config.yaml`.

## Current Status

Week 1 is complete and provides an analysis-ready foundation for Week 2, where the project will build the SQL metric layer:

* `user_metrics`
* `experiment_metrics`
* `guardrail_metrics`