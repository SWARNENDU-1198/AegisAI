# Codebase Concerns

**Analysis Date:** 2026-06-26

## Naming Anomaly

- **AI Package init file**: `backend/ai/init_.py` is named with a single trailing underscore instead of the Python standard `__init__.py` format. This can lead to module resolution issues or package import warnings depending on Python's path setup.

## Technical Debt & Performance Concerns

- **O(N) Database Queries in `file_service.py`**:
  - `save_files` runs a separate SELECT query for every single file in the scanned list to check if its path already exists in the database.
  - For directories with tens of thousands of files, this creates a massive N+1 query bottleneck.
- **Blocking Synchronous File Traversal**:
  - `scanner.py` and `hash_service.py` use synchronous operations (`Path.rglob` and `open().read()`).
  - Because FastAPI endpoints `/scan-and-save` and `/scan` are mapped directly to synchronous functions without background tasks or thread pools, crawling large user profiles will block the single-threaded event loop, leading to server unresponsiveness and HTTP timeouts.
- **Duplicate Database Files**:
  - There is an `aegisai.db` SQLite file in the root workspace and another one in the `backend/` directory. It is unclear which database is actively being targeted by the SQLite engine depending on the directory from which the app is run.

## Missing Quality Safeguards

- **Testing**: Complete absence of automated unit tests, integration tests, or mock objects.
- **Hardcoded Model**: The Gemini model string (`gemini-2.5-flash`) is hardcoded directly inside `backend/ai/gemini.py` instead of being configurable via environment variables or a configuration JSON.
- **Cyclic Directory Reference Protection**:
  - The recursive directories walk in `scanner.py` doesn't guard against recursive directories or symbolical link loops, which can lead to recursion stack overflows or infinite loops during crawling.
