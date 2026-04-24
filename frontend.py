
#frontEnd.py
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, date, timedelta
import re
import requests
app = Flask(__name__)

# In-memory data storage
# Each task has: id, group, title, due, priority
BACKEND_URL = "http://127.0.0.1:5001"
PASTEL_COLORS = ["#F9B7C9", "#B8F2D8","#FFE0C7","#C9C5FF","#B8F0F2","#E3B8F5",]

@app.route("/")
@app.route("/home")
def home():
    try:
        resp = requests.get(f"{BACKEND_URL}/api/tasks", timeout=3)
        resp.raise_for_status()
        all_tasks = resp.json()
    except Exception:
        return render_template("error.html")

    MAX_ITEMS = 20
    limited_tasks = all_tasks[:MAX_ITEMS]

    grouped = group_tasks(limited_tasks)
    return render_template("index.html", grouped_tasks=grouped)


@app.route("/new_task", methods=["GET", "POST"])
def new_task():
    if request.method == "POST":
        group = request.form.get("group", "").strip()
        title = request.form.get("title", "").strip()
        due = request.form.get("due", "").strip()
        priority_raw = request.form.get("priority", "").strip()

        errors = []

        # validation
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

        if errors:
            return render_template(
                "new_task.html",
                errors=errors,
                group=group,
                title=title,
                due=due,
                priority=priority_raw
            )

        payload = {
            "group": group,
            "title": title,
            "due": due,
            "priority": str(priority),
        }

        try:
            resp = requests.post(f"{BACKEND_URL}/api/tasks", json=payload, timeout=3)
            if resp.status_code >= 400:
                data = resp.json()
                backend_errors = data.get("errors", ["Backend validation failed."])
                return render_template(
                    "new_task.html",
                    errors=backend_errors,
                    group=group,
                    title=title,
                    due=due,
                    priority=priority_raw,
                )
        except Exception:
            return render_template("error.html")

        return redirect(url_for("home"))

    return render_template("new_task.html", errors=None)

#helper to validate dates
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
        return False, f"Due date must be within 5 years from today."
    return True, ""

# Group tasks by group name
def group_tasks(tasks):
    grouped = {}
    for t in tasks:
        group = t["group"]
        if group not in grouped:
            grouped[group] = []
        grouped[group].append(t)

    colored_groups = {}
    group_names = sorted(grouped.keys())
    for i, name in enumerate(group_names):
        color = PASTEL_COLORS[i % len(PASTEL_COLORS)]
        colored_groups[name] = {
            "color": color, "tasks": grouped[name]
        }
    return colored_groups

@app.route("/tasks/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    try:
        resp = requests.delete(f"{BACKEND_URL}/api/tasks/{task_id}", timeout=3)
        resp.raise_for_status()
    except Exception:
        return render_template("error.html")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
