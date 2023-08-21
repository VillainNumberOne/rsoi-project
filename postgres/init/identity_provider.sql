CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    user_uid        uuid UNIQUE NOT NULL,
    username        VARCHAR(100) NOT NULL,
    password_hash   VARCHAR(128) NOT NULL,
    user_role       INT NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);