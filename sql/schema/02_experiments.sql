CREATE TABLE IF NOT EXISTS experiments (
    experiment_id TEXT PRIMARY KEY,
    experiment_name TEXT NOT NULL,
    status TEXT NOT NULL,
    start_ts TIMESTAMP NOT NULL,
    end_ts TIMESTAMP NOT NULL,
    primary_metric TEXT NOT NULL,
    randomization_unit TEXT NOT NULL,
    control_label TEXT NOT NULL,
    treatment_label TEXT NOT NULL,
    hypothesis_direction TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
