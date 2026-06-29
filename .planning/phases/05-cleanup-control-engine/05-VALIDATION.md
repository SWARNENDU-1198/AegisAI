# Phase 5: Cleanup Control Engine - Validation

## Testing Plan

We will create a test suite `backend/test_cleanup.py` containing:

1. **Unit Tests for Duplicate Deletion Safety**:
   - Verify deletion request fails if `confirm=False`.
   - Verify deletion request fails if the target file is the last remaining copy in its duplicate group.
   - Verify successful deletion when `confirm=True` and multiple duplicates exist (file removed from disk, database record removed).

2. **Unit Tests for Temp Cleanup Safety**:
   - Verify temp cleanup fails if `confirm=False`.
   - Verify temp cleanup successfully deletes all temporary files, cleans database, and returns correct metrics when `confirm=True`.
