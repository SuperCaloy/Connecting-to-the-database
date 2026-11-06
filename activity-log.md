# Activity Log

- 2026-11-06: Initialized project infrastructure, requirements, design documentation, and Stage 0 SQLite connection with idempotent seeding.
- 2026-11-06: Completed Stage 1 with TDD; replaced in-memory reads in GET /tasks and GET /tasks/{id} with SQL SELECT queries.
- 2026-11-06: Completed Stage 2 with TDD; replaced array push in POST /tasks with SQL INSERT and verified persistence across restarts.
- 2026-11-06: Completed Stage 3 with TDD; implemented SQL UPDATE and DELETE in PUT /tasks/{id} and DELETE /tasks/{id}, and removed in-memory task lists.
- 2026-11-06: Completed Stage 4; executed manual SQL statements (SELECT, COUNT, UPDATE, DELETE) against tasks.db and verified immediate synchronization via API.

