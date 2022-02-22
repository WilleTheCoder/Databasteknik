-- Delete the tables if they exist.
-- Disable foreign key checks, so the tables can
-- be dropped in arbitrary order.
PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS theaters;

DROP TABLE IF EXISTS movies;

DROP TABLE IF EXISTS performances;

DROP TABLE IF EXISTS customers;

DROP TABLE IF EXISTS tickets;

PRAGMA foreign_keys = ON;

-- Create the tables.
CREATE TABLE theaters (
    theater_name VARCHAR(255),
    capacity INT,
    PRIMARY KEY (theater_name)
);

CREATE TABLE movies (
    imdb_key VARCHAR(255),
    title VARCHAR(255),
    year INT,
    PRIMARY KEY (imdb_key)
);

CREATE TABLE performances (
    performance_id TEXT DEFAULT (lower(hex(randomblob(16)))),
    date DATE,
    time TIME,
    imdb_key VARCHAR(255),
    theater_name VARCHAR(255),
    PRIMARY KEY (performance_id),
    FOREIGN KEY (imdb_key) REFERENCES movies(imdb_key),
    FOREIGN KEY (theater_name) REFERENCES theaters(theater_name)
);

CREATE TABLE customers (
    user_name VARCHAR(255),
    full_name VARCHAR(255),
    ticket_id VARCHAR(255),
    user_password VARCHAR(255),
    PRIMARY KEY (user_name),
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
);

CREATE TABLE tickets (
    ticket_id TEXT DEFAULT (lower(hex(randomblob(16)))),
    user_name VARCHAR(255),
    performance_id VARCHAR(255),
    PRIMARY KEY (ticket_id),
    FOREIGN KEY (user_name) REFERENCES customers(user_name),
    FOREIGN KEY (performance_id) REFERENCES performances(performance_id)
);

-- Insert data into the tables.
--THEATER
INSERT INTO
    theaters (theater_name, capacity)
VALUES
    ("Filmstaden lund S1", 100);

--MOVIES
INSERT INTO
    movies (imdb_key, title, year)
VALUES
    ("tt0076759", "Star Wars - A New Hope", 1977),
    (
        "tt0097576",
        "Indiana Jones and the Last Crusade",
        1989
    );

--performance
INSERT INTO
    performances (date, time, imdb_key, theater_name)
VALUES
    (
        "2022-02-09",
        "14:30:00",
        "tt0076759",
        "Filmstaden lund S1"
    ),
    (
        "2022-02-09",
        "19:00:00",
        "tt0097576",
        "Filmstaden lund S1"
    );

--customers
INSERT INTO
    customers (user_name, full_name, user_password)
VALUES
    ("TheBincher7", "Will Wilson", "wille123");