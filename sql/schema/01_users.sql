CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    signup_ts TIMESTAMP NOT NULL,
    country TEXT NOT NULL,
    platform TEXT NOT NULL,
    age_bucket TEXT NOT NULL,
    acquisition_channel TEXT NOT NULL,
    is_premium BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
