from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Path, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from database import init_db, reset_db


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

# Temporary in-memory fallback for Stage 0 while verifying DB init
tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read chapter 2", "done": True},
    {"id": 3, "title": "Write unit tests", "done": False},
]

next_id = 4


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
    result = tasks
    if done is not None:
        result = [t for t in result if t["done"] == done]
    if search:
        search_lower = search.lower()
        result = [t for t in result if search_lower in t["title"].lower()]
    return result


@app.get("/tasks/{id}", summary="Get task by ID")
def get_task(id: int = Path(..., description="The ID of the task to retrieve")):
    for task in tasks:
        if task["id"] == id:
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})


@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create a new task")
def create_task(payload: TaskCreate):
    global next_id
    new_task = {
        "id": next_id,
        "title": payload.title,
        "done": False,
    }
    next_id += 1
    tasks.append(new_task)
    return new_task


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

    for task in tasks:
        if task["id"] == id:
            if payload.title is not None:
                task["title"] = payload.title
            if payload.done is not None:
                task["done"] = payload.done
            return task

    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})


@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
def delete_task(id: int = Path(..., description="The ID of the task to delete")):
    for i, task in enumerate(tasks):
        if task["id"] == id:
            tasks.pop(i)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})


@app.post("/reset", summary="Reset tasks to initial state", include_in_schema=False)
def reset_tasks():
    global tasks, next_id
    tasks = [
        {"id": 1, "title": "Buy groceries", "done": False},
        {"id": 2, "title": "Read chapter 2", "done": True},
        {"id": 3, "title": "Write unit tests", "done": False},
    ]
    next_id = 4
    reset_db()
    return {"message": "Tasks reset to initial state"}

