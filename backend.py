
#backend.py -- pulled from source code
from flask import Flask, request, jsonify
import sqlite3
import json

# create the backend application, which only works with the database
backend_app = Flask(__name__)

# function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('../backend/database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ENDPOINTS
@backend_app.route("/api", methods=["GET"])
def get_all():
    # retrieve list from the database
    # connect to DB, run the SQL statement, close the connection
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM destinations').fetchall()
    conn.close()
    # the variable rows now contains a list of sqlite Row objects,
    # which needs to be converted to a list of dictionaries (i.e. json)
    result_list = [dict(row) for row in rows]
    # now we can send it to the json library to convert it to a string
    json_output = json.dumps(result_list, indent=4)
    return(json_output), 200  # creates response json, returns HTTP response 200

# create a new destination
@backend_app.route("/api/new", methods=["POST"])
def create_dest():
    # get info from POST request
    data = request.get_json()  # parses incoming json
    dest_name = data[0].get("name")
    # TODO: Input validation on all fields prior to database insertion!

    # Connect to DB and insert information
    conn = get_db_connection()
    conn.execute('INSERT INTO destinations (name, photo) VALUES (?, ?)',
                 (dest_name, "none"))
    conn.commit()
    conn.close()
    return jsonify({"name": dest_name}), 201  # creates response json, returns HTTP response 201
