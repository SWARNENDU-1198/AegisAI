# Phase 1: Database & Crawler Optimization - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-26
**Phase:** 1-Database & Crawler Optimization
**Areas discussed:** Background Task Mechanism, Database Bulk Operations, Scan Progress Storage, Concurrent Scan Policy

---

## Background Task Mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| FastAPI BackgroundTasks | Natively supported by FastAPI, runs in thread pool | |
| asyncio.create_task | Runs asynchronously in the FastAPI main event loop (needs executor for CPU-bound tasks) | ✓ |
| Standard threading module | Manually spawn a daemon thread | |

**User's choice:** asyncio.create_task
**Notes:** CPU-bound scanning/hashing needs to be scheduled inside an executor (e.g. `loop.run_in_executor`) to prevent blocking the event loop.

---

## Database Bulk Operations

| Option | Description | Selected |
|--------|-------------|----------|
| Set-based check + bulk_save_objects | Query all paths in a single SELECT query, check existence in memory, and insert in bulk | ✓ |
| Batching / Chunked checks | Query the database in chunks and insert in small batches | |

**User's choice:** Let Antigravity decide based on best practices (Set-based check + bulk operations).

---

## Scan Progress Storage

| Option | Description | Selected |
|--------|-------------|----------|
| In-memory state dictionary | Thread-safe dictionary stored in application memory | ✓ |
| SQLite scan_status table | Persist the scan status in a database table | |

**User's choice:** In-memory state dictionary.

---

## Concurrent Scan Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Block concurrent scans | Refuse new scans if one is already running | ✓ |
| Concurrent scans with unique IDs | Allow multiple scans to run concurrently | |

**User's choice:** Block concurrent scans.

## the agent's Discretion

Database bulk insert technology and structure details are left to the agent's discretion, utilizing SQLAlchemy best practices.

## Deferred Ideas

None.
