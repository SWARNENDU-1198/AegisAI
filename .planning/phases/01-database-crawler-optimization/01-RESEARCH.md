# Phase 1: Database & Crawler Optimization - Research

**Researched:** 2026-06-26
**Domain:** FastAPI, Python asyncio, SQLAlchemy 2.0, SQLite
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Use `asyncio.create_task` to spawn background tasks asynchronously from FastAPI endpoints.
- **D-02:** Run CPU-bound hashing and filesystem scanning in an executor (thread pool) using `loop.run_in_executor` (or `asyncio.to_thread`) to prevent blocking the asyncio event loop.
- **D-03:** Fetch all existing file paths from the SQLite database in a single query and load them into a set in memory for O(1) checks.
- **D-04:** Use SQLAlchemy bulk operations (e.g. `db.bulk_insert_mappings` or `db.bulk_save_objects`) to perform batch insertions of new file records, eliminating the N+1 query loop.
- **D-05:** Store background scan progress in an in-memory thread-safe dictionary within the FastAPI application state, tracking status (running, completed, failed), total files, processed count, and elapsed time.
- **D-06:** Block concurrent scans. If a scan is already running when a new scan is requested, return the current active scan task's ID and status rather than spawning a parallel scan.

### the agent's Discretion
- Database bulk insert technology and structure details utilizing SQLAlchemy best practices.

### Deferred Ideas (OUT OF SCOPE)
- None.

</user_constraints>

<research_summary>
## Summary

This research focuses on converting the blocking file crawler/hasher in AegisAI into an asynchronous background task using Python's `asyncio` and optimizing database insertions in SQLAlchemy 2.0.

Key findings:
1. File crawling (`pathlib.Path.rglob`) and file hashing (SHA-256) are I/O and CPU-intensive synchronous operations. Running them directly in an `async` function will block the FastAPI event loop. Running them via `asyncio.to_thread` delegates execution to a thread pool worker, keeping the main loop responsive.
2. SQLite database operations should use connection pools safely. The N+1 SELECT issue is resolved by querying all file paths up front (`session.query(FileRecord.path).all()`) and checking against a set in Python, followed by `db.bulk_insert_mappings(FileRecord, mappings)` which generates efficient `INSERT INTO ... VALUES ...` batches.

**Primary recommendation:** Implement a background runner that executes the crawl & hash in a worker thread (using `asyncio.to_thread`), updates an in-memory global state dict protected by a lock, and performs batch database saves using `db.bulk_insert_mappings`.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python asyncio | Built-in (3.14.3) | Asynchronous task orchestration and concurrency | Standard library concurrency |
| FastAPI | 0.136.3 | App framework, handles background execution and event loops | Standard framework in stack |
| SQLAlchemy | 2.0.50 | SQL Toolkit and Object Relational Mapper | Modern ORM with bulk insert support |
| SQLite | Built-in | Local relational database | Light local database |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `asyncio.create_task` | FastAPI `BackgroundTasks` | `asyncio.create_task` allows more fine-grained task-id tracking and lifecycle management than default FastAPI BackgroundTasks |
| `db.add_all` | `db.bulk_insert_mappings` | `bulk_insert_mappings` completely bypasses model instantiation overhead, executing orders of magnitude faster |

</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Recommended Project Structure
No structural changes needed; modifications will be applied to `backend/main.py`, `backend/services/file_service.py`, and `backend/scanner/scanner.py`.

### Pattern 1: Safe Background Task Execution with asyncio.to_thread
**What:** Offload CPU/IO intensive tasks to thread pool workers.
**Example:**
```python
import asyncio

async def run_scan_in_background(task_id: str, paths: list):
    # Delegate the synchronous blocking scan to a thread pool worker
    files = await asyncio.to_thread(scan_multiple_directories, paths)
    
    # Process files (hashing and saving) in a background thread
    await asyncio.to_thread(process_and_save_files, files)
```

### Pattern 2: SQLAlchemy 2.0 Bulk Insert
**What:** Set-based existence checks and batch insertion mappings.
**Example:**
```python
from database.db import SessionLocal
from database.models import FileRecord

def save_files_optimized(file_list):
    db = SessionLocal()
    try:
        # Step 1: Bulk check existing paths
        existing = {r[0] for r in db.query(FileRecord.path).all()}
        
        # Step 2: Filter new files
        to_insert = []
        for file in file_list:
            if file["path"] not in existing:
                to_insert.append({
                    "name": file["name"],
                    "path": file["path"],
                    "size": file["size"],
                    "extension": file["extension"],
                    "hash": file["hash"]
                })
        
        # Step 3: Bulk insert mappings
        if to_insert:
            db.bulk_insert_mappings(FileRecord, to_insert)
            db.commit()
    finally:
        db.close()
```

### Anti-Patterns to Avoid
- **Running CPU/IO bound code directly in async paths:** Writing `async def scan()` and calling `Path.rglob()` inside it blocks the entire FastAPI server because `Path.rglob` is synchronous and blocks the single thread running the asyncio loop.
- **SQLAlchemy N+1 insertion queries:** Querying `db.query(FileRecord).filter_by(path=p).first()` inside a loop for 10,000 files executes 10,000 queries, taking minutes instead of seconds.

</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Thread Pools | Custom thread pools/queues | `asyncio.to_thread` or `ThreadPoolExecutor` | Python standard library is robust, handles resource reclamation |
| Bulk DB mapping | Custom string-based SQL generation | SQLAlchemy `bulk_insert_mappings` | Prevents SQL injection, handles database dialect details automatically |

</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: SQLite Database Locked
**What goes wrong:** `sqlite3.OperationalError: database is locked`
**Why it happens:** SQLite allows multiple concurrent readers but only a single writer. Concurrent writes from threads block each other.
**How to avoid:** Block concurrent scans at the application level; use thread locks for updating in-memory status.

### Pitfall 2: Memory Bloat with Large File Lists
**What goes wrong:** High memory usage when processing hundreds of thousands of files.
**Why it happens:** Loading all path strings into a set in memory might consume tens of megabytes.
**How to avoid:** For SQLite/local machine scope (under 100k files), set-based checking is lightweight (~10MB memory). For millions of files, we would chunk or use index constraints, but for AegisAI local machine scan standard scope, a set is highly efficient and safe.

</common_pitfalls>

<sources>
## Sources

### Primary (HIGH confidence)
- Python `asyncio` official docs — task orchestration, `asyncio.to_thread`.
- FastAPI official docs — concurrency and background execution.
- SQLAlchemy 2.0 official docs — performance optimization, bulk insert operations.

</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: FastAPI, Python asyncio, SQLAlchemy
- Ecosystem: SQLite local persistence
- Patterns: Background task execution, bulk insert

**Confidence breakdown:**
- Standard stack: HIGH
- Architecture: HIGH
- Pitfalls: HIGH
- Code examples: HIGH

**Research date:** 2026-06-26
**Valid until:** 2026-07-26
</metadata>

---

*Phase: 01-database-crawler-optimization*
*Research completed: 2026-06-26*
*Ready for planning: yes*
