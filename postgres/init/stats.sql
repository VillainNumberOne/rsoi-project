CREATE TABLE stats (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(255),
    message_value TEXT,
    username VARCHAR(255),
    key VARCHAR(255),
    timestamp TIMESTAMP
);
