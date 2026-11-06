import pytest
from starlette.testclient import TestClient
from main import app
from database import get_connection, init_db, reset_db


@pytest.fixture(autouse=True)
def clean_db():
    reset_db()
    yield


def test_idempotent_seeding_multiple_starts():
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM tasks;").fetchone()[0]
        assert count == 3

    init_db()
    init_db()

    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM tasks;").fetchone()[0]
        assert count == 3
        rows = conn.execute("SELECT id, title, done FROM tasks ORDER BY id;").fetchall()
        assert rows[0]["title"] == "Buy groceries"
        assert rows[0]["done"] == 0
        assert rows[1]["title"] == "Read chapter 2"
        assert rows[1]["done"] == 1
        assert rows[2]["title"] == "Write unit tests"
        assert rows[2]["done"] == 0


def test_root_endpoint():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Task API"


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_tasks_reads_from_database():
    with get_connection() as conn:
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?);", ("Direct DB Task", 1))
        conn.commit()

    client = TestClient(app)
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    assert any(t["title"] == "Direct DB Task" and t["done"] is True for t in data)


def test_get_task_by_id_reads_from_database():
    client = TestClient(app)
    response = client.get("/tasks/1")
    assert response.status_code == 200
    data = response.json()
    assert data == {"id": 1, "title": "Buy groceries", "done": False}

    response_2 = client.get("/tasks/2")
    assert response_2.status_code == 200
    data_2 = response_2.json()
    assert data_2 == {"id": 2, "title": "Read chapter 2", "done": True}


def test_get_task_by_id_not_found():
    client = TestClient(app)
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"error": "Task 999 not found"}


def test_create_task_persists_in_database():
    client = TestClient(app)
    payload = {"title": "Learn SQLite"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 4
    assert data["title"] == "Learn SQLite"
    assert data["done"] is False

    # Check direct database persistence
    with get_connection() as conn:
        row = conn.execute("SELECT id, title, done FROM tasks WHERE id = 4;").fetchone()
        assert row is not None
        assert row["title"] == "Learn SQLite"
        assert row["done"] == 0


def test_create_task_validation():
    client = TestClient(app)
    # Empty title
    res_empty = client.post("/tasks", json={"title": ""})
    assert res_empty.status_code == 400
    assert "error" in res_empty.json()

    # Whitespace title
    res_ws = client.post("/tasks", json={"title": "   "})
    assert res_ws.status_code == 400
    assert "error" in res_ws.json()

    # Missing title field
    res_missing = client.post("/tasks", json={})
    assert res_missing.status_code == 400
    assert "error" in res_missing.json()


def test_create_task_survives_restart():
    client = TestClient(app)
    res = client.post("/tasks", json={"title": "Persistent Task"})
    assert res.status_code == 201
    task_id = res.json()["id"]

    # Simulate restart by re-initializing connection and app client without reset_db
    init_db()
    fresh_client = TestClient(app)
    get_res = fresh_client.get(f"/tasks/{task_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Persistent Task"
