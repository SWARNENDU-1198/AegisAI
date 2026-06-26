# Architecture

**Analysis Date:** 2026-06-26

## Pattern Overview

**Overall:** FastAPI Layered Backend Architecture

**Key Characteristics:**
- RESTful HTTP API endpoint interface
- Single-database SQLite backend with ORM layer
- Modular services separation (hashing, scanning, database saving, duplicate grouping, AI advice)
- Synchronous routing (endpoints load and run logic synchronously)

## Layers

**Router / Entry Layer:**
- **Purpose**: Defines Web endpoints, receives requests, and routes them to appropriate service layers.
- **Location**: `backend/main.py`
- **Depends on**: Service layer, Models layer, Scanner layer
- **Used by**: External API clients

**Service Layer:**
- **Purpose**: Implements core business logic for file hashing, database storage, duplicate grouping, and AI prompt generation.
- **Location**: `backend/services/*.py`
- **Depends on**: Database layer, AI layer
- **Used by**: Router layer

**Database Layer:**
- **Purpose**: Encapsulates DB connection session setup and SQLAlchemy ORM model definitions.
- **Location**: `backend/database/*.py`
- **Depends on**: SQLAlchemy core
- **Used by**: Service layer, Router layer

**AI Provider Layer:**
- **Purpose**: Manages interaction with Google Generative AI APIs.
- **Location**: `backend/ai/gemini.py`
- **Depends on**: `google-generativeai` package
- **Used by**: AI-dependent service modules (`ai_service.py`, `chat_service.py`)

**Scanner Layer:**
- **Purpose**: Core file-system crawler to index directories and metadata.
- **Location**: `backend/scanner/*.py`
- **Depends on**: Standard `pathlib` library
- **Used by**: Router layer (`main.py`)

## Data Flow

### Scan and Index Flow (e.g. `/scan-and-save`)
1. User invokes `/scan-and-save` endpoint in `backend/main.py`.
2. Router fetches `SCAN_PATHS` configuration from `backend/config.py`.
3. Router invokes `scan_multiple_directories` in `backend/scanner/scanner.py`.
4. Scanner walks target paths recursively via `Path.rglob` and collects files (name, path, size, suffix).
5. Router iterates through files, calling `calculate_hash` in `backend/services/hash_service.py` to get SHA-256 signatures.
6. Router calls `save_files` in `backend/services/file_service.py`.
7. `save_files` writes non-existent paths to SQLite `files` table and commits.
8. JSON response is returned to the user.

### Chat Flow (`/chat`)
1. User posts a natural language question to `/chat` with JSON body `{ "question": "..." }`.
2. Router parses body as `ChatRequest` Pydantic model.
3. Router invokes `answer_question` in `backend/services/chat_service.py`.
4. Service queries SQLite DB via `get_storage_analysis()`, `get_largest_files()`, and `find_duplicates()`.
5. Service formats database metrics into a detailed prompt template.
6. Service calls `ask_ai` in `backend/ai/gemini.py` to get a structured response from Gemini.
7. Router returns the answer in a JSON response.

## Key Abstractions

**SQLAlchemy ORM Model:**
- **Purpose**: Represents a DB table row as a Python object.
- **Example**: `FileRecord` in `backend/database/models.py`.

**Service Functions:**
- **Purpose**: Exposes decoupled operational routines.
- **Examples**: `find_duplicates()`, `calculate_hash()`, `save_files()`.

## Entry Points

**FastAPI App Instance:**
- **Location**: `backend/main.py`
- **Triggers**: Start command (e.g., `uvicorn main:app --reload`)
- **Responsibilities**: Initialize API router, run database setup (`create_tables`), and handle requests.

## Error Handling

**Strategy:** Safe fallback and exception swallow.
- Hashing and file scanning wrap file system access in try/except blocks to ignore inaccessible files or directories (e.g., permissions errors).
- Database operations ensure connections are closed cleanly in `finally` blocks.
- Gemini API errors are caught in `backend/ai/gemini.py` and returned as safe string warnings (`"AI Error: ..."`) to prevent server crashes.

## Cross-Cutting Concerns

**Configuration**:
- `backend/config.py` lists default folders (`SCAN_PATHS`) to scan.
- `.env` lists environment secrets.
