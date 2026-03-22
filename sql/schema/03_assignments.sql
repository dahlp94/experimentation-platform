CREATE TABLE IF NOT EXISTS assignments (
    assignment_id BIGSERIAL PRIMARY KEY,
    experiment_id TEXT NOT NULL REFERENCES experiments (experiment_id),
    user_id BIGINT NOT NULL REFERENCES users (user_id),
    variant TEXT NOT NULL,
    assigned_ts TIMESTAMP NOT NULL,
    assignment_channel TEXT NOT NULL DEFAULT 'randomizer',
    is_eligible BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_assignments_experiment_user UNIQUE (experiment_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_assignments_experiment_variant ON assignments (experiment_id, variant);
CREATE INDEX IF NOT EXISTS idx_assignments_user_id ON assignments (user_id);
