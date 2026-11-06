# Design Notes

## System Architecture
The Task API follows a layered architecture:
1. **HTTP / API Layer:** FastAPI app in `main.py` routing HTTP requests, handling validation errors, and serializing responses.
2. **Data Access Layer:** `database.py` manages connections to `tasks.db`, schema initialization, and transactional queries.
3. **Storage Engine:** SQLite 3 database engine embedded locally as `tasks.db`.

## Data Flow
- Clients send HTTP requests to `/tasks` endpoints.
- FastAPI validates requests using Pydantic models.
- Endpoint handlers acquire a SQLite connection via `database.get_connection()`.
- SQL queries are executed and row tuples mapped to dictionaries with boolean conversion (`bool(row["done"])`).
- Serialized responses are returned with exact HTTP status codes.

