# Task API — Persistent SQLite Backend

A lightweight RESTful CRUD API built with FastAPI and backed by a persistent SQLite database (`tasks.db`). This project replaces the in-memory task storage from Assignment 1 with a relational SQLite database while keeping every endpoint, request body, response shape, and HTTP status code completely identical.

---

## Why SQLite was Chosen

1. **Zero External Daemon Required:** SQLite is an embedded, serverless, self-contained relational database engine. There is no separate database server process to install, configure, or administer.
2. **Persistence Across Process Lifecycles:** Data written to `tasks.db` survives application reboots, crashes, and host restarts.
3. **Standard SQL Compliant:** Supports ACID transactions, primary key auto-increment constraints, check constraints, and standard ANSI SQL (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `LIKE`).
4. **Lightweight & Portable:** The entire database lives in a single portable file on disk, making testing and local development fast and frictionless.

---

## Database File Storage

- **Filename:** `tasks.db`
- **Location:** Project root (`d:\Project\Flyrank\A2 Connecting to the database\tasks.db`)
- **Schema (Third Normal Form - 3NF):**

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL CHECK (done IN (0, 1)) DEFAULT 0
);
```

### Table Structure Viewer

```
+-------------------------------------------------------------------------+
|                              tasks.db                                   |
+----+-----------------------+------+-------------------------------------+
| id | title                 | done | notes                               |
+----+-----------------------+------+-------------------------------------+
|  1 | Buy groceries         | 0    | Initial seed task (False)           |
|  2 | Read chapter 2        | 1    | Initial seed task (True)            |
|  3 | Write unit tests      | 0    | Initial seed task (False)           |
+----+-----------------------+------+-------------------------------------+
```

---

## Installation & Startup from Scratch

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Setup Virtual Environment
```powershell
# Clone or navigate to the repository directory
cd "d:\Project\Flyrank\A2 Connecting to the database"

# Create a Python 3.11 virtual environment
py -3.11 -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run the API Server
```powershell
uvicorn main:app --reload --port 8000
```
The server will start at `http://127.0.0.1:8000`. On first run, it automatically creates `tasks.db` and seeds the 3 example tasks idempotently.

### 5. Run the Automated Tests
```powershell
pytest -v
```

---

## API Contract Specification

All endpoints remain identical to Assignment 1:

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/health` | Health check endpoint | `200 OK` |
| `GET` | `/tasks` | List all tasks | `200 OK` |
| `GET` | `/tasks?done=true` | Filter tasks by completion | `200 OK` |
| `GET` | `/tasks?search=unit` | Search tasks by title | `200 OK` |
| `GET` | `/tasks/{id}` | Get task by ID | `200 OK` (or `404 Not Found`) |
| `POST` | `/tasks` | Create a new task | `201 Created` (or `400 Bad Request`) |
| `PUT` | `/tasks/{id}` | Update existing task | `200 OK` (or `400 Bad Request`, `404 Not Found`) |
| `DELETE` | `/tasks/{id}` | Delete task | `204 No Content` (or `404 Not Found`) |

Interactive Swagger documentation is available at `http://127.0.0.1:8000/docs`.

---

## Manual SQL Exploration (Stage 4)

The database was explored directly using standard SQL queries and cross-verified against live API output:

### 1. Select all tasks
```sql
SELECT * FROM tasks;
```
**Output:**
```
id | title            | done
---+------------------+-----
 1 | Buy groceries    | 0
 2 | Read chapter 2   | 1
 3 | Write unit tests | 0
```

### 2. Select completed tasks
```sql
SELECT * FROM tasks WHERE done = 1;
```
**Output:**
```
id | title          | done
---+----------------+-----
 2 | Read chapter 2 | 1
```

### 3. Count total tasks
```sql
SELECT COUNT(*) FROM tasks;
```
**Output:**
```
3
```

### 4. Update all tasks to done
```sql
UPDATE tasks SET done = 1;
```
**Live API Verification (`GET /tasks`):**
```json
[
  {"id": 1, "title": "Buy groceries", "done": true},
  {"id": 2, "title": "Read chapter 2", "done": true},
  {"id": 3, "title": "Write unit tests", "done": true}
]
```

### 5. Delete all completed tasks
```sql
DELETE FROM tasks WHERE done = 1;
```
**Live API Verification (`GET /tasks`):**
```json
[]
```

