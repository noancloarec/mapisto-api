CREATE SCHEMA mapisto;

SET search_path TO mapisto;

CREATE TABLE States(
    state_id serial PRIMARY KEY
);

CREATE TABLE StateNames(
    name VARCHAR(255),
    state_id INTEGER REFERENCES states(state_id),
    validity_start TIMESTAMP NOT NULL,
    validity_end TIMESTAMP NOT NULL,
    color VARCHAR(6)
);

CREATE TABLE Territories(
    territory_id serial PRIMARY KEY,
    d_path TEXT NOT NULL,
    precision_in_km REAL NOT NULL,
    validity_start TIMESTAMP NOT NULL,
    validity_end TIMESTAMP NOT NULL,
    state_id INTEGER REFERENCES states(state_id)
);
