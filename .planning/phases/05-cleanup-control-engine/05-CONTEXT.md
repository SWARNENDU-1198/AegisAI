# Phase 5: Cleanup Control Engine - Context

**Gathered:** 2026-06-26
**Status:** Ready for planning
**Source:** Autonomous Phase Initialization

<domain>
## Phase Boundary

This phase implements user-triggered cleanup actions for duplicates and temporary/junk files in AegisAI. It delivers endpoints for deletion that require mandatory user confirmation parameters.

### Scoped In:
- POST endpoint `/delete-duplicate` accepting file `path`, `duplicate_hash`, and a mandatory `confirm: bool = False`.
  - Verifies that the file exists and is indeed a duplicate belonging to the specified hash group.
  - Deletes the file from the local file system.
  - Removes the record from the database.
- POST endpoint `/cleanup-temp` accepting a mandatory `confirm: bool = False`.
  - Identifies files categorized as `"Temp"`.
  - Deletes them from disk and database.
  - Returns counts of files deleted and total bytes recovered.

### Scoped Out / Deferred:
- Auto-cleanup (never allowed under system safety constraints).
- System Recycle Bin integration (direct `os.remove` is sufficient).
</domain>

<decisions>
## Implementation Decisions

### 1. Mandatory Confirmation
- All cleanup endpoints must fail with `400 Bad Request` or require `confirm=True` explicitly in query/payload parameters.

### 2. Double-Check Verification
- When deleting a duplicate, check if there is at least one other file with the same hash in the database to prevent deleting the *only* copy of a file!
- Return a `400 Bad Request` if the user tries to delete the last copy of a duplicate group.

### 3. Database Sync
- Deletions are executed inside database transaction blocks. On failure, disk removals are not rolled back, but database records are kept in sync with actual disk state.
</decisions>

<canonical_refs>
## Canonical References

- [main.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/main.py) — API endpoints.
- [file_service.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/services/file_service.py) — DB persistence and file deletion service.
</canonical_refs>
