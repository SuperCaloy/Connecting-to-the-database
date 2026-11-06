from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Path, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from database import get_connection, init_db, reset_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Task API",
    description="A lightweight RESTful CRUD API for managing tasks backed by SQLite.",
    version="1.0",
    lifespan=lifespan,
)


def task_row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


class TaskCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title is required and cannot be empty or whitespace only")
        return v.strip()


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("Title cannot be empty or whitespace only")
            return v.strip()
        return v


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_msg = "Invalid request payload"
    for err in exc.errors():
        msg = err.get("msg", "")
        if "Value error," in msg:
            error_msg = msg.replace("Value error,", "").strip()
            break
        elif err.get("type") == "missing":
            loc = ".".join(str(item) for item in err.get("loc", []) if item != "body")
            error_msg = f"{loc or 'Field'} is required"
            break
        elif msg:
            error_msg = msg
            break
    return JSONResponse(status_code=400, content={"error": error_msg})


@app.get("/", summary="API Root Metadata")
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": [
            "/health",
            "/tasks",
            "/tasks/{id}",
            "/docs",
        ],
    }


@app.get("/health", summary="Health Check")
def get_health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def get_tasks(
    done: Optional[bool] = None,
    search: Optional[str] = None,
):
    query = "SELECT id, title, done FROM tasks"
    params = []
    conditions = []

    if done is not None:
        conditions.append("done = ?")
        params.append(1 if done else 0)

    if search:
        conditions.append("LOWER(title) LIKE ?")
        params.append(f"%{search.lower()}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY id ASC;"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [task_row_to_dict(r) for r in rows]


@app.get("/tasks/{id}", summary="Get task by ID")
def get_task(id: int = Path(..., description="The ID of the task to retrieve")):
    with get_connection() as conn:
        row = conn.execute("SELECT id, title, done FROM tasks WHERE id = ?;", (id,)).fetchone()
        if row is not None:
            return task_row_to_dict(row)
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})


@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create a new task")
def create_task(payload: TaskCreate):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, 0);", (payload.title,))
        conn.commit()
        new_id = cursor.lastrowid
        return {
            "id": new_id,
            "title": payload.title,
            "done": False,
        }


@app.put("/tasks/{id}", summary="Update an existing task")
def update_task(
    payload: TaskUpdate,
    id: int = Path(..., description="The ID of the task to update"),
):
    if payload.title is None and payload.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "At least one field (title or done) must be provided"},
        )

    with get_connection() as conn:
        cursor = conn.cursor()
        existing = cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?;", (id,)).fetchone()
        if existing is None:
            return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

        new_title = payload.title if payload.title is not None else existing["title"]
        new_done = (1 if payload.done else 0) if payload.done is not None else existing["done"]

        cursor.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?;",
            (new_title, new_done, id),
        )
        conn.commit()

        return {
            "id": id,
            "title": new_title,
            "done": bool(new_done),
        }


@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
def delete_task(id: int = Path(..., description="The ID of the task to delete")):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?;", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/reset", summary="Reset tasks to initial state", include_in_schema=False)
def reset_tasks():
    reset_db()
    return {"message": "Tasks reset to initial state"}

