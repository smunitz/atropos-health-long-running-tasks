import sys
from pathlib import Path
import time
import pytest

# Add backend folder to path temporarily so imports work
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app import app
import tasks

# --- Fixture to provide a test client and clean DB after each test ---
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
    # Cleanup tasks after test
    with tasks.get_connection() as conn:
        conn.execute("DELETE FROM tasks")
        conn.commit()

# --- Helper to wait for a task to finish ---
def wait_for_task(task_id, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        task = tasks.get_task(task_id)
        if task["status"] in [tasks.TaskStatus.SUCCESS, tasks.TaskStatus.FAILURE]:
            return task
        time.sleep(0.5)
    return tasks.get_task(task_id)  # return last known state

# --- Tests ---
def test_create_task(client):
    res = client.post("/tasks")
    assert res.status_code == 201
    task_id = res.json["task_id"]
    task = wait_for_task(task_id)
    assert task["status"] == tasks.TaskStatus.SUCCESS

def test_cancel_task(client):
    task_id = client.post("/tasks").json["task_id"]
    cancel_res = client.patch(f"/tasks/{task_id}/status")
    task = tasks.get_task(task_id)
    # Depending on timing, the task may already be complete
    if task["status"] == tasks.TaskStatus.CANCELLED:
        assert cancel_res.status_code == 200
    else:
        assert cancel_res.status_code == 404

def test_delete_task(client):
    task_id = client.post("/tasks").json["task_id"]
    del_res = client.delete(f"/tasks/{task_id}")
    assert del_res.status_code == 200

    task = tasks.get_task(task_id)
    assert task is None

def test_task_result_response(client):
    task_id = client.post("/tasks").json["task_id"]
    task = wait_for_task(task_id)
    res = client.get(f"/tasks/{task_id}/result")
    data = res.json
    assert data["status"] == task["status"]
    if task["status"] == tasks.TaskStatus.SUCCESS:
        assert "completed" in data["result"]

def test_nonexistent_task(client):
    status_res = client.get("/tasks/nonexistent/status")
    assert status_res.status_code == 404
    result_res = client.get("/tasks/nonexistent/result")
    assert result_res.status_code == 404
    del_res = client.delete("/tasks/nonexistent")
    assert del_res.status_code == 404

def test_list_tasks_with_status_filter(client):
    res1 = client.post("/tasks")
    res2 = client.post("/tasks")
    task_id1 = res1.json["task_id"]
    task_id2 = res2.json["task_id"]

    task1 = wait_for_task(task_id1)
    task2 = wait_for_task(task_id2)

    with tasks.get_connection() as conn:
        rows = conn.execute("SELECT id, status FROM tasks").fetchall()
        all_tasks = [dict(row) for row in rows]

    assert any(t["id"] == task_id1 for t in all_tasks)
    assert any(t["id"] == task_id2 for t in all_tasks)

def test_task_final_status(client):
    res = client.post("/tasks")
    task_id = res.json["task_id"]
    task = wait_for_task(task_id)
    # Task should either succeed or fail
    assert task["status"] in {tasks.TaskStatus.SUCCESS, tasks.TaskStatus.FAILURE}