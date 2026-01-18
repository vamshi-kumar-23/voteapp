from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

# ================== CONFIG ==================
VOTING_DEADLINE = datetime(2026, 1, 20, 18, 0, 0)
DB_NAME = "database.db"

app = Flask(__name__)
app.secret_key = "voting_secret"

# ================== DB HELPER ==================
def get_db():
    return sqlite3.connect(DB_NAME)

# ================== LOGIN ==================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]

            if username == "admin":
                return redirect("/admin")
            return redirect("/vote")

    return render_template("login.html")

# ================== VOTE PAGE ==================
@app.route("/vote")
def vote():
    if "username" not in session:
        return redirect("/")

    if session["username"] == "admin":
        return redirect("/admin")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()
    conn.close()

    return render_template("vote.html", candidates=candidates)

# ================== CAST VOTE ==================
@app.route("/cast_vote/<int:candidate_id>")
def cast_vote(candidate_id):
    if "username" not in session:
        return redirect("/")

    # Deadline check
    if datetime.now() > VOTING_DEADLINE:
        return redirect("/vote?status=ended")

    # Admin cannot vote
    if session["username"] == "admin":
        return redirect("/admin")

    user_id = session["user_id"]

    conn = get_db()
    cursor = conn.cursor()

    # Check if already voted
    cursor.execute("SELECT has_voted FROM users WHERE id=?", (user_id,))
    voted = cursor.fetchone()

    if voted and voted[0] == 1:
        conn.close()
        return redirect("/vote?status=already_voted")

    # Cast vote
    cursor.execute(
        "UPDATE candidates SET votes = votes + 1 WHERE id=?",
        (candidate_id,)
    )

    cursor.execute(
        "UPDATE users SET has_voted = 1 WHERE id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/vote?status=voted")

# ================== RESULT PAGE ==================
@app.route("/result")
def result():
    if "username" not in session:
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT result_declared FROM settings WHERE id=1")
    declared = cursor.fetchone()[0]

    # Block students before declaration
    if session["username"] != "admin" and declared == 0:
        conn.close()
        return "<h3>⏳ Results not declared yet. Please wait.</h3>"

    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()

    max_votes = max([c[2] for c in candidates]) if candidates else 0

    conn.close()

    return render_template(
        "result.html",
        candidates=candidates,
        max_votes=max_votes
    )

# ================== DECLARE RESULT ==================
@app.route("/declare_result")
def declare_result():
    if "username" not in session or session["username"] != "admin":
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE settings SET result_declared = 1 WHERE id=1")
    conn.commit()
    conn.close()

    return redirect("/result")

# ================== ADMIN PANEL ==================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "username" not in session or session["username"] != "admin":
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["candidate"]
        cursor.execute("INSERT INTO candidates (name) VALUES (?)", (name,))
        conn.commit()

    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()
    conn.close()

    return render_template("admin.html", candidates=candidates)

# ================== LOGOUT ==================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================== RUN ==================
if __name__ == "__main__":
    app.run(debug=True)
