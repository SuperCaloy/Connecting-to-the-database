from pathlib import Path
import sqlite3
from typing import Generator

DB_PATH = Path(__file__).resolve().parent / "tasks.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL CHECK (done IN (0, 1)) DEFAULT 0
            );
            """
        )
        cursor.execute("SELECT COUNT(*) FROM tasks;")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?);",
                [
                    ("Buy groceries", 0),
                    ("Read chapter 2", 1),
                    ("Write unit tests", 0),
                ],
            )
            conn.commit()


def reset_db() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS tasks;")
        conn.commit()
    init_db()

