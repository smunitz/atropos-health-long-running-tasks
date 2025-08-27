import sqlite3
import threading

DB_FILE = "tasks.db"
DB_LOCK = threading.Lock()  # prevent concurrent write issues

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                result TEXT
            )
        """)
        conn.commit()