# Design Decisions

## 1. Storage Engine Choice: SQLite 3 Standard Library
- **Decision:** Use Python standard library `sqlite3` without ORM overhead.
- **Alternatives Considered:** SQLModel, SQLAlchemy, Tortoise ORM.
- **Tradeoffs:** Raw SQL requires explicit query strings and manual row-to-dict mappings, but avoids heavy external dependencies, ensures zero compile overhead, and directly models standard SQL statements required by curriculum checkpoints.
- **Reason:** Fits KISS and DRY principles, fulfills all assignment requirements cleanly.

## 2. Idempotent Database Seeding
- **Decision:** Execute `SELECT COUNT(*) FROM tasks` before inserting seed data.
- **Alternatives Considered:** Flag file on disk, `INSERT OR IGNORE` with hardcoded IDs.
- **Tradeoffs:** Checking count allows seeding only on fresh installations. If a user deletes all tasks later, a manual reset endpoint is provided rather than re-seeding on next reboot.
- **Reason:** Keeps application startup predictable and avoids overwriting user modifications.

