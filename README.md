# Experimentation Platform

A production-style experimentation platform that models the full lifecycle of A/B testing: data generation, assignment, behavioral logging, validation, and reproducible pipelines.

This project is designed to demonstrate both statistical rigor and industry-level system design, bridging the gap between experimental methodology and production data workflows.

---

## Project Overview

Modern experimentation systems require more than computing metrics. They require:

- correct assignment design
- reliable event logging
- reproducible data pipelines
- integrity validation
- structured outputs for downstream analysis

This project builds that foundation end-to-end.

---

## Week 1: Data Foundation (Completed)

Week 1 establishes a robust and reproducible experimentation data layer.

### Key Components

- **Relational Schema**
  - Four core tables: `users`, `experiments`, `assignments`, `events`
  - Indexing and constraint enforcement
  - Unique constraint on `(experiment_id, user_id)` to ensure valid randomization

- **Synthetic Data Pipeline**
  - Config-driven simulation using YAML
  - Deterministic random generation via seeded RNG
  - Realistic behavioral event generation

- **Data Engineering Workflow**
  - Schema creation via SQL scripts
  - CSV-based intermediate storage
  - Bulk loading into PostgreSQL
  - Idempotent reload process

- **Validation and Testing**
  - Pytest-based integrity tests
  - Assignment correctness validation
  - Event consistency checks
  - Experiment window enforcement

---

## Data Model

| Table | Description |
|------|------------|
| **users** | User-level attributes including signup time, country, platform, and segmentation features |
| **experiments** | Experiment metadata including time window, metric, and variant labels |
| **assignments** | Variant assignment per user; one row per user per experiment |
| **events** | Raw behavioral logs such as sessions, page views, conversions, and purchases |

Additional fields:

- `event_value`: numeric payload (e.g., purchase amount)
- `metadata_json`: structured context for events

---

## Design Principles

### 1. Separation of Assignment and Behavior
Assignments are recorded once and independently of user actions. Behavioral outcomes are logged separately, ensuring clean causal structure.

### 2. User-Level Randomization
Each user receives exactly one assignment per experiment, enforced via database constraints.

### 3. Event-Driven Architecture
Events are stored as raw logs, enabling flexible downstream aggregation and analysis without recomputation.

### 4. Reproducibility
All data generation is controlled by configuration and a fixed random seed, ensuring consistent outputs across runs.

### 5. Experiment Window Integrity
All post-assignment events are constrained within the experiment window, preventing temporal leakage into analysis.

---

## How to Run

### Prerequisites
- Python 3.11+
- PostgreSQL
- Valid `DATABASE_URL`

---

### 1. Environment Setup

```bash
cp .env.example .env
# Set DATABASE_URL in .env
# Example:
# postgresql://user:password@localhost:5432/exp_platform

python -m venv venv_exp_platform
source venv_exp_platform/bin/activate
pip install -r requirements.txt
````

---

### 2. Create Schema

```bash
python scripts/create_schema.py
```

---

### 3. Generate Synthetic Data

```bash
python scripts/generate_synthetic_data.py
```

---

### 4. Load Data into PostgreSQL

```bash
python scripts/load_synthetic_data.py
```

---

### 5. Verify Data Integrity

```bash
python scripts/verify_seed_data.py
```

---

### 6. Run Tests

```bash
pytest tests/
```

---

## Data Integrity Guarantees

* One assignment per `(experiment_id, user_id)`
* Assignment and behavioral data are strictly separated
* All experiment-period events occur within the experiment window
* Pre-period events occur strictly before assignment
* Synthetic data generation is fully reproducible

---

## Simulation Logic

1. Generate users with attributes and signup timestamps prior to experiment start
2. Create experiment metadata from configuration
3. Assign users based on traffic fraction and treatment probability
4. Generate session activity between assignment and experiment end
5. Simulate behavioral funnel:

   * session_start
   * page_view
   * optional add_to_cart
   * optional conversion
   * purchase with positive value
6. Optionally simulate pre-period activity before assignment

All parameters are configurable via:

```text
configs/simulation_config.yaml
```

---

## Current Status

Week 1 is complete and provides a clean, validated, and reproducible data foundation.

Next steps (Week 2):

* Build SQL metric layer:

  * `user_metrics`
  * `experiment_metrics`
  * `guardrail_metrics`
* Construct analysis-ready datasets for statistical inference
