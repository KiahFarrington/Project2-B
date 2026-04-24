
#backend.py -- pulled from source code
from flask import Flask, request, jsonify
import sqlite3
import re
from datetime import datetime, timedelta, date
import json

backend_app = Flask(__name__)
DB_NAME = "tasks.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks ( id INTEGER PRIMARY KEY AUTOINCREMENT, group_name TEXT NOT NULL, title TEXT NOT NULL, due TEXT NOT NULL, priority INTEGER NOT NULL);
        """
    )
    conn.commit()
    conn.close()


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


@backend_app.route("/api/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, group_name, title, due, priority FROM tasks ORDER BY priority ASC, id ASC"
    )
    rows = cur.fetchall()
    conn.close()

    tasks = []
    for r in rows:
        tasks.append(
            {
                "id": r["id"],
                "group": r["group_name"],
                "title": r["title"],
                "due": r["due"],
                "priority": r["priority"],
            }
        )
    return jsonify(tasks), 200


@backend_app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json() or {}
    errors, group, title, due, priority = validate_task_payload(data)

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (group_name, title, due, priority) VALUES (?, ?, ?, ?)",
        (group, title, due, priority),
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True}), 201


@backend_app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True}), 200


if __name__ == "__main__":
    init_db()
    backend_app.run(debug=True, port=5001)