# Phase 5: Cleanup Control Engine - Research

## File Deletion Python Standard APIs
We will use standard `os.remove(path)` or `pathlib.Path(path).unlink(missing_ok=True)`.

## Deletion Safety Checks

### 1. Duplicate Deletion Safety Check
Before removing a duplicate file:
1. Verify the file record exists in the SQLite database by querying the `path`.
2. Verify the record's `hash` matches the client-supplied `duplicate_hash`.
3. Query the database for the total count of file records matching this `hash`:
   - If count <= 1, abort. This is the last remaining copy! Deleting it would result in data loss.
4. Delete file from file system.
5. Delete record from database.

### 2. Temp Deletion Safety Check
Before removing temp files:
1. Query database for all records where `category == "Temp"`.
2. Loop and delete each file from the file system.
3. Delete records from the database in bulk or one-by-one inside a transaction.
4. Calculate and return total size of deleted files.
