import pytest
from starlette.testclient import TestClient
from main import app
from database import get_connection, init_db, reset_db


@pytest.fixture(autouse=True)
def clean_db():
    reset_db()
    yield


def test_idempotent_seeding_multiple_starts():
    # Initial run seeds 3 tasks
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM tasks;").fetchone()[0]
        assert count == 3

    # Subsequent init calls must not insert duplicate rows
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

