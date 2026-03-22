# Experimentation platform

This repository holds an experimentation platform focused on trustworthy assignment, raw behavioral events, and reproducible synthetic data. Week 1 establishes the relational data foundation: PostgreSQL schema, a config-driven simulator, CSV exports, bulk load scripts, and integrity tests.

## Week 1 completed

- **Schema:** four tables (`users`, `experiments`, `assignments`, `events`) with indexes and a unique constraint on `(experiment_id, user_id)` for assignments.
- **Synthetic pipeline:** YAML config, numpy-seeded generator, CSV export under `data/synthetic/`.
- **Database workflow:** apply DDL, load CSVs in dependency order, verification script for quick sanity checks.
- **Validation:** pytest coverage for generator shape, assignment rules, and event consistency.

## Data model

| Table | Role |
| ----- | ---- |
| **users** | Stable user dimensions (signup time, country, platform, segments, premium flag). |
| **experiments** | Metadata for each test (window, metric, labels, randomization unit). |
| **assignments** | Which variant each user received and when; one row per user per experiment. |
| **events** | Timestamped raw logs (`session_start`, `page_view`, `add_to_cart`, `conversion`, `purchase`, optional pre-period activity). |

`event_value` carries numeric payload when relevant (purchase amount). `metadata_json` holds small structured context as JSON.

## Why this design is correct

- **Assignments and behavior are separate:** variant exposure is recorded once in `assignments`; outcomes live in `events`, avoiding a single denormalized table that mixes design and response.
- **User-level randomization:** the unique constraint on `(experiment_id, user_id)` enforces one assignment per user for the experiment, matching the configured randomization unit.
- **Events as raw logs:** rows resemble production-style streams for sessions and funnel steps, which later supports SQL metrics and inference without re-simulating.
- **Reproducibility:** `random_seed` in `configs/simulation_config.yaml` plus centralized RNG construction makes runs repeatable for tests and demos.

## How to run

Prerequisites: Python 3.11+, PostgreSQL, and a database URL.

1. **Environment**

   ```bash
   cp .env.example .env
   # Set DATABASE_URL in .env, e.g. postgresql://user:pass@localhost:5432/experimentation_platform
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create schema**

   ```bash
   python scripts/create_schema.py
   ```

3. **Generate synthetic CSVs**

   ```bash
   python scripts/generate_synthetic_data.py
   ```

4. **Load into Postgres**

   ```bash
   python scripts/load_synthetic_data.py
   ```

5. **Verify loaded data**

   ```bash
   python scripts/verify_seed_data.py
   ```

6. **Tests**

   ```bash
   pytest tests/
   ```

The load script truncates `events`, `assignments`, `experiments`, and `users` (with identity restart) before inserting, so re-running produces a clean reload.

## Simulation logic (short)

1. Draw `n_users` with categorical attributes and signup times before the experiment window.
2. Emit one experiment row from config.
3. Assign users according to `traffic_fraction` and `treatment_probability`; assignment timestamps fall inside `[start_ts, end_ts]`.
4. For each assigned user, draw session counts (Poisson with mean `mean_sessions_per_user`, at least one), place session starts between assignment and experiment end, then emit funnel events. Conversion is Bernoulli with variant-specific probability; at most one `conversion` per user, with a following `purchase` and positive `event_value` when they convert. Optional pre-period `session_start` / `page_view` events occur strictly after signup and before assignment.

Tune behavior in `configs/simulation_config.yaml`.
