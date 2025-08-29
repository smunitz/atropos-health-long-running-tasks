# Atropos Health – Long Running Tasks API

## Overview

This project implements a **backend API and minimal frontend** for managing long-running tasks. It supports:

- Creating tasks
- Checking task status
- Retrieving task results
- Canceling tasks
- Deleting tasks

The frontend is a **vanilla JS dashboard** showing tasks in real time with optional status filtering.

---

## API Endpoints

| Method   | Endpoint                  | Description                                      |
| -------- | ------------------------- | ------------------------------------------------ |
| `POST`   | `/tasks`                  | Create a new task                                |
| `GET`    | `/tasks`                  | List all tasks (optional status filter)          |
| `GET`    | `/tasks/<task_id>/status` | Get current task status                          |
| `PATCH`  | `/tasks/<task_id>/status` | Cancel a task (marks CANCELLED, result retained) |
| `GET`    | `/tasks/<task_id>/result` | Retrieve task result or error                    |
| `DELETE` | `/tasks/<task_id>`        | Permanently remove a task                        |
| `GET`    | `/health`                 | Basic service health check                       |

---

## Tech & Architecture

- **Flask** backend for a lightweight API
- **SQLite** for persistence (task state survives restarts), though current dashboard only displays tasks created during the current session
- **Background threads** simulate long-running tasks
  - For production can use Celery + Redis or a managed task queue
- **Frontend**: Minimal dashboard served by Flask; polls tasks every second
- **Docker**: Single container for easy deployment
- Health check ensures container auto-restarts if the service is unhealthy

**Notes:**

- Frontend and backend share the same origin for minimal complexity in this demo
- Polling is simple but not scalable
- PATCH endpoint currently only cancels tasks, but can be extended

---

## Running

### Requirements

- Python 3.11
- Flask (installed via `requirements.txt`)
- Docker
- Pytest for testing

### Build image

```bash
docker build -t flask-tasks .
```

### Run container

```bash
docker run -p 5000:5000 flask-tasks
```

Access the dashboard at http://localhost:5000

## Testing

Run tests with pytest:

```python
python -m pytest tests
```
