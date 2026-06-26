<!-- GSD:project-start source:PROJECT.md -->
## Project

**AegisAI**

AegisAI is an AI-powered Digital Intelligence Platform that understands, organizes, secures, and optimizes a user's computer. It is not a file cleaner; rather, it acts as an intelligent operating layer for Windows that understands the user's digital life.

**Core Value:** Provides a safe, intelligent digital assistant that helps users understand, search, and optimize their local machine's files, storage, and security without automated destructive changes.

### Constraints

- **Operating System**: Windows - Tailored for Windows file directories and structures.
- **Tech Stack**: Python (3.14.3), FastAPI, SQLAlchemy, SQLite, and Google Gemini.
- **Security & Data Safety**: All AI recommendations are advisory; destructive actions must be user-validated.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages and Runtimes
- **Python**: 3.14.3 (runs in `venv` virtual environment)
## Backend Framework
- **FastAPI**: 0.136.3 (used for Web API routing and application server)
- **Uvicorn**: 0.49.0 (ASGI web server implementation)
## Database and ORM
- **SQLite**: Built-in Python database, stores file records locally in `aegisai.db`
- **SQLAlchemy**: 2.0.50 (Object Relational Mapper for database modeling and queries)
## AI Libraries
- **Google Generative AI (`google-generativeai`)**: 0.8.6 (used to communicate with Google Gemini API)
## Other Core Dependencies
- **Pydantic**: 2.13.4 (data validation and settings management using python type annotations)
- **python-dotenv**: 1.2.2 (reads key-value pairs from a `.env` file and sets them as environment variables)
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Python Syntax & Code Style
- **Version Guidelines**: Runs on Python 3.14.3.
- **Form**: Python code is organized into modular directories with module folders containing logic.
- **Import Abstraction**:
## Error Handling Patterns
- **Silent Catch (File System / Disk operations)**:
- **Error Propagation (API / AI Provider)**:
## Database Interaction
- **Session Context Lifecycle**:
## Dependency Configuration
- Paths config: Crawler path configurations are stored in list variables (`SCAN_PATHS` in `backend/config.py`).
- Environments: Environment configurations (API keys) are kept in `.env` and loaded using `python-dotenv`.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- RESTful HTTP API endpoint interface
- Single-database SQLite backend with ORM layer
- Modular services separation (hashing, scanning, database saving, duplicate grouping, AI advice)
- Synchronous routing (endpoints load and run logic synchronously)
## Layers
- **Purpose**: Defines Web endpoints, receives requests, and routes them to appropriate service layers.
- **Location**: `backend/main.py`
- **Depends on**: Service layer, Models layer, Scanner layer
- **Used by**: External API clients
- **Purpose**: Implements core business logic for file hashing, database storage, duplicate grouping, and AI prompt generation.
- **Location**: `backend/services/*.py`
- **Depends on**: Database layer, AI layer
- **Used by**: Router layer
- **Purpose**: Encapsulates DB connection session setup and SQLAlchemy ORM model definitions.
- **Location**: `backend/database/*.py`
- **Depends on**: SQLAlchemy core
- **Used by**: Service layer, Router layer
- **Purpose**: Manages interaction with Google Generative AI APIs.
- **Location**: `backend/ai/gemini.py`
- **Depends on**: `google-generativeai` package
- **Used by**: AI-dependent service modules (`ai_service.py`, `chat_service.py`)
- **Purpose**: Core file-system crawler to index directories and metadata.
- **Location**: `backend/scanner/*.py`
- **Depends on**: Standard `pathlib` library
- **Used by**: Router layer (`main.py`)
## Data Flow
### Scan and Index Flow (e.g. `/scan-and-save`)
### Chat Flow (`/chat`)
## Key Abstractions
- **Purpose**: Represents a DB table row as a Python object.
- **Example**: `FileRecord` in `backend/database/models.py`.
- **Purpose**: Exposes decoupled operational routines.
- **Examples**: `find_duplicates()`, `calculate_hash()`, `save_files()`.
## Entry Points
- **Location**: `backend/main.py`
- **Triggers**: Start command (e.g., `uvicorn main:app --reload`)
- **Responsibilities**: Initialize API router, run database setup (`create_tables`), and handle requests.
## Error Handling
- Hashing and file scanning wrap file system access in try/except blocks to ignore inaccessible files or directories (e.g., permissions errors).
- Database operations ensure connections are closed cleanly in `finally` blocks.
- Gemini API errors are caught in `backend/ai/gemini.py` and returned as safe string warnings (`"AI Error: ..."`) to prevent server crashes.
## Cross-Cutting Concerns
- `backend/config.py` lists default folders (`SCAN_PATHS`) to scan.
- `.env` lists environment secrets.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.agent/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
