CREATE SCHEMA mapisto;

SET search_path TO mapisto;

CREATE TABLE states(
    state_id SERIAL PRIMARY KEY,
    validity_start TIMESTAMP NOT NULL,
    validity_end TIMESTAMP NOT NULL
);

CREATE TABLE state_names(
    name VARCHAR(255),
    state_id INTEGER REFERENCES states(state_id) ON DELETE CASCADE,
    validity_start TIMESTAMP NOT NULL,
    validity_end TIMESTAMP NOT NULL,
    color VARCHAR(7)
);

CREATE TABLE territories(
    territory_id SERIAL PRIMARY KEY,
    validity_start TIMESTAMP NOT NULL,
    validity_end TIMESTAMP NOT NULL,
    min_x REAL NOT NULL,
    max_x REAL NOT NULL,
    min_y REAL NOT NULL,
    max_y REAL NOT NULL,
    name VARCHAR(255),
    color VARCHAR(7),
    state_id INTEGER REFERENCES states(state_id) ON DELETE CASCADE
);

CREATE TABLE territories_shapes(
    d_path TEXT NOT NULL,
    precision_in_km NUMERIC(6, 1) NOT NULL,
    territory_id INTEGER REFERENCES territories(territory_id) ON DELETE CASCADE,
    PRIMARY KEY (precision_in_km, territory_id)
);

CREATE TABLE lands(
    land_id SERIAL PRIMARY KEY,
    min_x REAL NOT NULL,
    max_x REAL NOT NULL,
    min_y REAL NOT NULL,
    max_y REAL NOT NULL
);

CREATE TABLE lands_shapes(
    d_path TEXT NOT NULL,
    precision_in_km NUMERIC(6,1) NOT NULL,
    land_id INTEGER REFERENCES lands(land_id) ON DELETE CASCADE,
    PRIMARY KEY (precision_in_km, land_id)
);
