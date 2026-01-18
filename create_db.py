import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ================== USERS TABLE ==================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    has_voted INTEGER DEFAULT 0
)
""")

# ================== CANDIDATES TABLE ==================
cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    votes INTEGER DEFAULT 0
)
""")

# ================== SETTINGS TABLE ==================
cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY,
    result_declared INTEGER DEFAULT 0
)
""")

# ================== INITIAL SETTINGS ==================
cursor.execute(
    "INSERT OR IGNORE INTO settings (id, result_declared) VALUES (1, 0)"
)

# ================== USERS ==================
users = [
    ("student1", "123"),
    ("student2", "123"),
    ("student3", "123"),
    ("student4", "123"),
    ("student5", "123"),
    ("admin", "admin")
]

for u in users:
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
        u
    )

# ================== CANDIDATES ==================
candidates = ["Candidate A", "Candidate B"]

for c in candidates:
    cursor.execute(
        "INSERT OR IGNORE INTO candidates (name) VALUES (?)",
        (c,)
    )

conn.commit()
conn.close()

print("✅ Database created / updated successfully!")
