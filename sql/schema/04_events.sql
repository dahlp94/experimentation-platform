CREATE TABLE IF NOT EXISTS events (
    event_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users (user_id),
    experiment_id TEXT REFERENCES experiments (experiment_id),
    event_ts TIMESTAMP NOT NULL,
    event_name TEXT NOT NULL,
    session_id TEXT,
    event_value NUMERIC(12, 2),
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_events_experiment_user ON events (experiment_id, user_id);
CREATE INDEX IF NOT EXISTS idx_events_event_name ON events (event_name);
CREATE INDEX IF NOT EXISTS idx_events_event_ts ON events (event_ts);
