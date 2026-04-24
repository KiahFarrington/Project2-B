
#backend.py -- pulled from source code
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, timedelta, date
import json

def validate_due_date(due_str):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", due_str):
        return False, "Due date must be in YYYY-MM-DD format."
    try:
        dt = datetime.strptime(due_str, "%Y-%m-%d").date()
    except ValueError:
        return False, "Due date is not a valid calendar date."
    min_date = date(2024, 1, 1)
    max_date = date.today() + timedelta(days=365 * 5)
    if dt < min_date:
        return False, "Due date cannot be earlier than 2024."
    if dt > max_date:
        return False, "Due date must be within 5 years from today."
    return True, ""

def validate_task_payload(data):
    errors = []

    group = (data.get("group") or "").strip()
    title = (data.get("title") or "").strip()
    due = (data.get("due") or "").strip()
    priority_raw = (data.get("priority") or "").strip()

    if not group or len(group) > 50:
        errors.append("Group is required and must be less than 50 characters.")
    if not title or len(title) > 100:
        errors.append("Task title is required and must be less than 100 characters.")

    if not due:
        errors.append("Due date is required.")
    else:
        ok, msg = validate_due_date(due)
        if not ok:
            errors.append(msg)

    priority = None
    if not priority_raw:
        errors.append("Priority is required.")
    else:
        try:
            priority = int(priority_raw)
            if priority < 1 or priority > 4:
                errors.append("Priority must be an integer between 1 and 4.")
        except ValueError:
            errors.append("Priority must be an integer.")

    return errors, group, title, due, priority
backend_app = Flask(__name__)
DB_NAME = "tasks.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
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
