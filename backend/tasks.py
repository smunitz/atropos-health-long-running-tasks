import threading
import time
import uuid
from enum import Enum

from db import get_connection, DB_LOCK

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    CANCELLED = "CANCELLED"

def long_running_task(task_id: str):
    """Simulate a long job that writes result to DB"""
    try:
        with DB_LOCK, get_connection() as conn:
            conn.execute("UPDATE tasks SET status=? WHERE id=?", (TaskStatus.RUNNING, task_id))
            conn.commit()

        for _ in range(10):
            with get_connection() as conn:
                row = conn.execute("SELECT status FROM tasks WHERE id=?", (task_id,)).fetchone()
                if row["status"] == TaskStatus.CANCELLED:
                    return
            time.sleep(1)

        result_data = f"Task {task_id} completed successfully!"

        with DB_LOCK, get_connection() as conn:
            conn.execute(
                "UPDATE tasks SET status=?, result=? WHERE id=?",
                (TaskStatus.SUCCESS, result_data, task_id)
            )
            conn.commit()

    except Exception as e:
        with DB_LOCK, get_connection() as conn:
            conn.execute(
                "UPDATE tasks SET status=?, result=? WHERE id=?",
                (TaskStatus.FAILURE, str(e), task_id)
            )
            conn.commit()

def create_task():
    """Insert a new task and start background thread"""
    task_id = str(uuid.uuid4())
    with DB_LOCK, get_connection() as conn:
        conn.execute(
            "INSERT INTO tasks (id, status) VALUES (?, ?)",
            (task_id, TaskStatus.PENDING)
        )
        conn.commit()

    thread = threading.Thread(target=long_running_task, args=(task_id,))
    thread.start()
    return task_id

def get_task(task_id: str):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        return dict(row) if row else None

def get_all_tasks():
    """Return a list of all tasks"""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM tasks").fetchall()
        return [dict(row) for row in rows]

def cancel_task(task_id: str):
    """Mark a task as CANCELLED. Returns True if task exists, False otherwise."""
    with DB_LOCK, get_connection() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET status=? WHERE id=? AND status!=?",
            (TaskStatus.CANCELLED, task_id, TaskStatus.CANCELLED)
        )
    conn.commit()
    return cursor.rowcount > 0

def delete_task(task_id: str):
    """Remove a task from the DB. Returns True if removed, False otherwise."""
    with DB_LOCK, get_connection() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0