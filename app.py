
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, date, timedelta
import re
app = Flask(__name__)

# In-memory data storage
# Each task has: id, group, title, due, priority
tasks = [
    {"id": 1, "group": "CS 101", "title": "Read Chapter 3","due": "2025-04-21","priority": 2},
    {"id": 2,"group": "Life","title": "Do laundry","due": "2025-04-22","priority": 3} ]
PASTEL_COLORS = [
    "#F9B7C9", 
    "#B8F2D8",
    "#FFE0C7",
    "#C9C5FF",
    "#B8F0F2",
    "#E3B8F5",
]

@app.route("/")
@app.route("/home")
def home():
    # sort by priority (lower number = higher priority)
    sorted_tasks = sorted(tasks, key=lambda t: t["priority"])
    grouped = group_tasks(sorted_tasks)
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

        new_id = len(tasks) + 1
        tasks.append({
            "id": new_id,
            "group": group,
            "title": title,
            "due": due,
            "priority": priority
        })
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
            "color": color,
            "tasks": grouped[name]
        }
    return colored_groups

@app.route("/tasks/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    for t in tasks:
        if t["id"] == task_id:
            tasks.remove(t)
            break
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
