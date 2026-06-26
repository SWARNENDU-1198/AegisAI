# Phase 1: Database & Crawler Optimization - Context

**Gathered:** 2026-06-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Optimize database indexing queries (`CORE-05`) and implement asynchronous background disk scans and hashing tasks (`CORE-06`) to ensure the server remains responsive and does not block the FastAPI HTTP event loop.

</domain>

<decisions>
## Implementation Decisions

### Background Task Mechanism
- **D-01:** Use `asyncio.create_task` to spawn background tasks asynchronously from FastAPI endpoints.
- **D-02:** Run CPU-bound hashing and filesystem scanning in an executor (thread pool) using `loop.run_in_executor` to prevent blocking the asyncio event loop.

### Database Bulk Operations
- **D-03:** Fetch all existing file paths from the SQLite database in a single query and load them into a set in memory for O(1) checks.
- **D-04:** Use SQLAlchemy bulk operations (e.g. `db.bulk_insert_mappings` or `db.bulk_save_objects`) to perform batch insertions of new file records, eliminating the N+1 query loop.

### Scan Progress Storage
- **D-05:** Store background scan progress in an in-memory thread-safe dictionary within the FastAPI application state, tracking status (running, completed, failed), total files, processed count, and elapsed time.

### Concurrent Scan Policy
- **D-06:** Block concurrent scans. If a scan is already running when a new scan is requested, return the current active scan task's ID and status rather than spawning a parallel scan.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & Roadmap
- `.planning/REQUIREMENTS.md` — Defines CORE-05 and CORE-06 requirements.
- `.planning/ROADMAP.md` — Defines Phase 1 goal and success criteria.

### Existing Code base
- `backend/main.py` — FastAPI endpoints (`/scan-and-save`).
- `backend/services/file_service.py` — Database save logic.
- `backend/scanner/scanner.py` — Crawling functions.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/scanner/scanner.py` — functions `scan_multiple_directories` and `scan_directory` already implement filesystem crawling using `pathlib`.
- `backend/services/hash_service.py` — `calculate_hash` handles SHA-256 calculation.
- `backend/database/db.py` — `SessionLocal` for DB sessions.

### Established Patterns
- Services separation: hashing, database saving, and crawler modules are decoupled in `backend/services` and `backend/scanner`.

### Integration Points
- `/scan-and-save` in `backend/main.py` is modified to start the background task.
- `/scan-status/{task_id}` is a new endpoint in `backend/main.py` to retrieve scan status.

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-database-crawler-optimization*
*Context gathered: 2026-06-26*
