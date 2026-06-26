# Code Conventions

**Analysis Date:** 2026-06-26

## Python Syntax & Code Style

- **Version Guidelines**: Runs on Python 3.14.3.
- **Form**: Python code is organized into modular directories with module folders containing logic.
- **Import Abstraction**:
  - The codebase utilizes fallback `try/except` imports to allow files to be executed both as standalone scripts and as nested submodules under FastAPI.
  ```python
  try:
      from ..database.db import SessionLocal
      from ..database.models import FileRecord
  except Exception:
      from database.db import SessionLocal
      from database.models import FileRecord
  ```
  - Absolute import paths from `backend` root are standard fallbacks.

## Error Handling Patterns

- **Silent Catch (File System / Disk operations)**:
  - File path crawler (`scanner.py`) and hash calculation (`hash_service.py`) wrap operations in blank try-catch blocks to prevent breaking on permission-restricted files or corrupt paths.
  ```python
  try:
      # File operation
  except Exception:
      pass  # Swallows exception to continue directory traversal
  ```
- **Error Propagation (API / AI Provider)**:
  - Gemini client wrapper catches raw exceptions and transforms them into user-friendly error strings rather than crashing.
  ```python
  except Exception as e:
      return f"AI Error: {str(e)}"
  ```

## Database Interaction

- **Session Context Lifecycle**:
  - Services instantiate DB sessions dynamically via `SessionLocal()`.
  - To prevent connection pool exhaustion, queries are wrapped in `try/finally` blocks, with the session explicitly closed in the `finally` clause.
  ```python
  db = SessionLocal()
  try:
      # Perform DB actions
  finally:
      db.close()
  ```

## Dependency Configuration

- Paths config: Crawler path configurations are stored in list variables (`SCAN_PATHS` in `backend/config.py`).
- Environments: Environment configurations (API keys) are kept in `.env` and loaded using `python-dotenv`.
