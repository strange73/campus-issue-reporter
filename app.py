from flask import Flask, request, jsonify, render_template, g
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "issues.db")

CATEGORIES = ["Electrical", "Plumbing", "Furniture", "Cleanliness", "Internet/Wi-Fi", "Other"]
STATUSES = ["Open", "In Progress", "Fixed"]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            upvotes INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html", categories=CATEGORIES, statuses=STATUSES)


@app.route("/api/issues", methods=["GET"])
def list_issues():
    status_filter = request.args.get("status")
    category_filter = request.args.get("category")
    sort = request.args.get("sort", "recent")

    query = "SELECT * FROM issues WHERE 1=1"
    params = []
    if status_filter and status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)
    if category_filter and category_filter != "All":
        query += " AND category = ?"
        params.append(category_filter)

    if sort == "upvotes":
        query += " ORDER BY upvotes DESC, created_at DESC"
    else:
        query += " ORDER BY created_at DESC"

    db = get_db()
    rows = db.execute(query, params).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/issues", methods=["POST"])
def create_issue():
    data = request.get_json(force=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    category = (data.get("category") or "").strip()
    location = (data.get("location") or "").strip()

    if not title or not category or not location:
        return jsonify({"error": "Title, category and location are required."}), 400
    if category not in CATEGORIES:
        return jsonify({"error": "Invalid category."}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO issues (title, description, category, location, status, upvotes, created_at) "
        "VALUES (?, ?, ?, ?, 'Open', 0, ?)",
        (title, description, category, location, datetime.utcnow().isoformat()),
    )
    db.commit()
    new_row = db.execute("SELECT * FROM issues WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(new_row)), 201


@app.route("/api/issues/<int:issue_id>/status", methods=["PATCH"])
def update_status(issue_id):
    data = request.get_json(force=True) or {}
    new_status = data.get("status")
    if new_status not in STATUSES:
        return jsonify({"error": "Invalid status."}), 400

    db = get_db()
    row = db.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Issue not found."}), 404

    db.execute("UPDATE issues SET status = ? WHERE id = ?", (new_status, issue_id))
    db.commit()
    updated = db.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
    return jsonify(dict(updated))


@app.route("/api/issues/<int:issue_id>/upvote", methods=["POST"])
def upvote_issue(issue_id):
    db = get_db()
    row = db.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Issue not found."}), 404

    db.execute("UPDATE issues SET upvotes = upvotes + 1 WHERE id = ?", (issue_id,))
    db.commit()
    updated = db.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
    return jsonify(dict(updated))


@app.route("/api/issues/<int:issue_id>", methods=["DELETE"])
def delete_issue(issue_id):
    db = get_db()
    db.execute("DELETE FROM issues WHERE id = ?", (issue_id,))
    db.commit()
    return jsonify({"ok": True})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
else:
    init_db()
