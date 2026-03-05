import sqlite3
import os
from contextlib import contextmanager

DB_FILE = "khetipulse.db"

def init_db():
    """Initializes the SQLite database and creates the users table."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT,
                full_name TEXT,
                mobile_number TEXT,
                google_id TEXT UNIQUE,
                picture TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

@contextmanager
def get_db():
    """Provides a thread-safe SQLite connection."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Initialize on module load
if not os.path.exists(DB_FILE):
    init_db()
