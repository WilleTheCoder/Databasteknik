import sqlite3
from anyio import start_blocking_portal
from bottle import get, post, run, request, response
from urllib.parse import unquote

db = sqlite3.connect("mov.sqlite")

tables = ["theaters", "movies", "performances", "customers", "tickets"]

def hash(msg):
    import hashlib
    return hashlib.sha256(msg.encode('utf-8')).hexdigest()

# PING
@get("/ping")
def ping():
    response.status = 200
    return "pong"

# RESET
@post("/reset")
def reset():
    c = db.cursor()
    for t in tables:
        c.execute(
            """
        DELETE FROM %s
        """ % t)

    c.execute(
        """
        INSERT INTO theaters
        ("theater_name", "capacity")
        VALUES
        ("Kino", 10),
        ("Regal", 16),
        ("Skandia", 100)
        """
    )
    db.commit()
    return "reset tables"

# POST-USERS
@post("/users")
def addUser():
    req = request.json
    c = db.cursor()

    c.execute(
        """
        SELECT user_name
        FROM customers
        WHERE user_name = ?
        """, [req["username"]]
    )
    user = req["username"]
    found = c.fetchone()
    if found:
        response.status = 400
        return ""
    else:
        c.execute(
            """
            INSERT INTO customers
            (user_name, full_name, user_password)
            VALUES
            (?, ?, ?)
            """,
            [req["username"], req["fullName"], hash(req["pwd"])]
        )
        db.commit()
        response.status = 201
        return f"/users/{user}"

# POST-MOVIES
@post("/movies")
def addMovie():
    req = request.json
    c = db.cursor()

    c.execute(
        """
        SELECT imdb_key
        FROM movies
        WHERE imdb_key = ?
        """, [req["imdbKey"]]
    )
    imdbKey = req["imdbKey"]
    found = c.fetchone()
    if found:
        response.status = 400
        return ""
    else:
        c.execute(
            """
                INSERT INTO movies
                (imdb_key, title, year)
                VALUES
                (?, ?, ?)
                """,
            [req["imdbKey"], req["title"], req["year"]]
        )
        db.commit()
        response.status = 201
        return f"/movies/{imdbKey}"

# POST-PERFORMANCE
@post("/performances")
def addPerformance():
    req = request.json
    c = db.cursor()

    c.execute(
        """
        SELECT imdb_key
        FROM movies
        WHERE imdb_key = ?
        """, [req["imdbKey"]]
    )
    imdbKey = c.fetchone()

    c.execute(
        """
        SELECT theater_name
        FROM theaters
        WHERE theater_name = ?
        """, [req["theater"]]
    )
    theaterName = c.fetchone()

    if not(imdbKey) or not(theaterName):
        response.status = 400
        return "No such movie or theater"
    else:
        c.execute(
            """
            INSERT INTO performances
            (date, time, imdb_key, theater_name)
            VALUES
            (?, ?, ?, ?)
            """,
            [req["date"], req["time"], req["imdbKey"], req["theater"]]
        )
    db.commit()
    response.status = 201

    c.execute(
        """
        SELECT performance_id
        from performances
        WHERE rowid = last_insert_rowid()
        """
    )
    id = c.fetchone()

    return f"/performances/{id}"

# GET-MOVIES
@get('/movies')
def get_movie_search():
    query = """
        SELECT   imdb_key, title, year
        FROM     movies
        WHERE    1 = 1
        """
    params = []
    if request.query.title:
        query += " AND title = ?"
        params.append(unquote(request.query.title))
    if request.query.year:
        query += " AND year = ?"
        params.append(request.query.year)

    c = db.cursor()
    c.execute(query, params)
    found = [{"imdbKey": imdb_key, "title": title, "year": year}
             for imdb_key, title, year in c]
    response.status = 200
    return {"data": found}

# GET-MOVIES-IMDB
@get('/movies/<imdb_key>')
def getMovieFromImdb(imdb_key):
    c = db.cursor()
    c.execute(
        """
        SELECT imdb_key, title, year
        FROM movies
        WHERE imdb_key = ?   
        """,
        [imdb_key]
    )
    found = [{"imdbKey": imdb_key, "title": title, "year": year}
             for imdb_key, title, year in c]
    response.status = 200
    return {"data": found}


# GET-PERFORMANCE
@get('/performances')
def getPerformances():
    c = db.cursor()
    c.execute(
        """
        WITH seatsTaken(performance_id, takenSeats) AS (
            SELECT performance_id, COUNT(*) AS takenSeats
            FROM tickets t
            JOIN performances p
            USING (performance_id)
            GROUP BY performance_id
        )
        SELECT performance_id, date, time, title, year, theater_name, capacity - coalesce(takenSeats, 0) AS remainingSeats
        FROM performances 
        JOIN movies
        USING (imdb_key)
        JOIN theaters
        USING (theater_name)
        LEFT OUTER JOIN seatsTaken
        USING (performance_id)
        """
    )
    found = [{"performanceId": performance_id, "date": date, "time": time, "title": title,
              "year": year, "theater": theater_name, "remainingSeats": remainingSeats}
             for performance_id, date, time, title, year, theater_name, remainingSeats in c]

    return {"data": found}

# POST TICKETS
@post("/tickets")
def addTicket():
    req = request.json
    c = db.cursor()
    c.execute(
        """
        WITH seatsTaken(performance_id, takenSeats) AS (
            SELECT performance_id, COUNT(*) AS takenSeats
            FROM tickets t
            JOIN performances p
            USING (performance_id)
            GROUP BY performance_id
        )
        SELECT capacity - coalesce(takenSeats, 0) AS remainingSeats
        FROM performances 
        JOIN movies
        USING (imdb_key)
        JOIN theaters
        USING (theater_name)
        LEFT OUTER JOIN seatsTaken
        USING (performance_id)
        WHERE performance_id = ?
        """,
        [req["performanceId"]]
    )
    seats = c.fetchone()
    if seats is not None:
        if seats[0] <= 0:
            response.status = 400
            return "No tickets left"

    c.execute(
        """
        SELECT user_password
        FROM customers
        WHERE user_name = ?
        """,
        [req["username"]]
    )
    passw = c.fetchone()

    if not hash(req["pwd"]) == passw[0]:
        response.status = 401
        return "Wrong user credentials"

    c.execute(
        """
        SELECT performance_id
        FROM performances
        WHERE performance_id = ?
        """,
        [req["performanceId"]]
    )
    found = c.fetchone()
    if not found:
        response.status = 400
        return "Error"

    c.execute(
        """
        INSERT INTO
        tickets
        ("user_name", "performance_id")
        VALUES
        (?, ?)
        """,
        [req["username"], req["pwd"]]
    )
    response.status = 201

    c.execute(
        """
        SELECT ticket_id
        FROM tickets
        WHERE rowid = last_insert_rowid()
        """
    )
    ticket_id = c.fetchone()
    return "/tickets/"+ticket_id[0]

# GET-USERS-USERNAME-TICKETS
@get("/users/<username>/tickets")
def getUsers(username):
    c = db.cursor()
    c.execute(
        """
        WITH ticket_count AS (
            SELECT  performance_id, count(ticket_id) AS bought_tickets
            FROM    performances
            LEFT OUTER JOIN  tickets USING(performance_id)
            WHERE   user_name = ?
            GROUP BY  performance_id
        )
        SELECT    date, time, theater_name, title, year, bought_tickets
        FROM      performances
        JOIN      movies USING (imdb_key)
        JOIN      ticket_count USING (performance_id)
        JOIN      theaters USING (theater_name)
        """,
        [username]
    )
    found = [{"date": date, "startTime": time, "theater": theater_name, "title": title, "year": year, "nbrOfTickets": nbrOfTickets}
             for date, time, theater_name, title, year, nbrOfTickets in c]
    response.status = 200
    return {"data": found}


#################
# GET-USERS
@get("/users")
def getUser():
    c = db.cursor()
    c.execute(
        """
        SELECT user_name, full_name, ticket_id, user_password
        FROM customers
        """
    )
    found = [{"username": user_name, "fullName": full_name, "ticketId": ticket_id, "pwd": user_password}
             for user_name, full_name, ticket_id, user_password in c]

    return {"data": found}


run(host="localhost", port=7007)
