# Project Requirements

## Overview
Week 3 Assignment 1: Connect the Task CRUD API to a persistent SQLite database (`tasks.db`) replacing in-memory array storage while maintaining strictly identical endpoints, payloads, status codes, and error semantics.

## Functional Requirements
- **FR1 (Database Initialization):** On server startup, create table `tasks` if it does not exist.
- **FR2 (Idempotent Seeding):** If table `tasks` is empty on startup, insert three initial tasks:
  1. `Buy groceries` (done: false)
  2. `Read chapter 2` (done: true)
  3. `Write unit tests` (done: false)
  Seed tasks must not be duplicated across restarts.
- **FR3 (Read Operations):**
  - `GET /tasks`: Retrieve all tasks from `tasks.db` with status 200.
  - `GET /tasks/{id}`: Retrieve single task by id with status 200. Return 404 if not found.
- **FR4 (Create Operation):**
  - `POST /tasks`: Validate non-empty title; insert into `tasks.db`; return status 201 with newly created task. Return 400 on validation failure.
- **FR5 (Update Operation):**
  - `PUT /tasks/{id}`: Update title and/or done status in `tasks.db`; return status 200. Return 404 if not found, 400 if invalid.
- **FR6 (Delete Operation):**
  - `DELETE /tasks/{id}`: Delete task from `tasks.db`; return status 204 with no body. Return 404 if not found.

