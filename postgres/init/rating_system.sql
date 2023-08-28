CREATE TABLE rating
(
    id       SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    stars    INT         NOT NULL CHECK (stars BETWEEN 0 AND 100)
);
