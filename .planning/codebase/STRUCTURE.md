# Directory Structure

**Analysis Date:** 2026-06-26

## Project Root Layout

```
AegisAI/
├── .git/                      # Git repository metadata
├── .gitignore                 # Specifies intentionally untracked files to ignore
├── .planning/                 # GSD planning directory (this folder)
│   └── codebase/              # Codebase maps and technical notes
├── aegisai.db                 # Database file (created at runtime in root)
├── backend/                   # Backend Python web service application
│   ├── .env                   # Local configuration environment secrets
│   ├── main.py                # App entry point, API route registry
│   ├── config.py              # Configuration values (crawling path array)
│   ├── test_ai.py             # Script to verify connection to Gemini API
│   ├── ai/                    # AI LLM wrappers
│   ├── database/              # Database models, schemas, and session managers
│   ├── models/                # Pydantic schemas for data serialization
│   ├── scanner/               # Disk scanning implementation
│   └── services/              # Business logic layers
└── venv/                      # Python 3.14.3 virtual environment
```

## Backend Folder Structure

### `backend/ai/`
- `gemini.py` - Connects to `gemini-2.5-flash` model and handles raw API execution.
- `init_.py` - Package initialization (Note: Named `init_.py` rather than standard `__init__.py`).

### `backend/database/`
- `db.py` - Establishes SQLite SQLAlchemy database engine and local session creator.
- `init_db.py` - Helper to create database tables schema if they do not exist.
- `models.py` - Declares SQLAlchemy ORM schema mapping for `files` table (`FileRecord`).

### `backend/models/`
- `chat_models.py` - Declares Pydantic data request and response models for `/chat` endpoint.

### `backend/scanner/`
- `scanner.py` - Directory traversal module that recursively indexes files and file metadata.

### `backend/services/`
- `ai_service.py` - Combines database storage statistics and feeds them to Gemini to get cleaning advice.
- `chat_service.py` - Provides contextual responses to freeform user questions using storage metadata.
- `duplicate_service.py` - Analyzes indexed file hashes and groups identical files.
- `file_service.py` - Bulk saves new file indices to the SQLite database.
- `hash_service.py` - Helper to calculate SHA-256 signatures for local files.
- `storage_service.py` - Queries database for general stats (count, total size) and largest files.
