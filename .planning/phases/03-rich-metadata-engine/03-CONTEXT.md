# Phase 3: Rich Metadata Engine - Context

**Gathered:** 2026-06-26
**Status:** Ready for planning
**Source:** Autonomous Phase Initialization

<domain>
## Phase Boundary

This phase implements rich metadata extraction for image, audio, PDF, and Office document files in AegisAI. It delivers database schema modifications, background crawler integration, and a dedicated metadata retrieval endpoint.

### Scoped In:
- Schema modification of the `files` table to include a `meta_data` column (JSON string).
- Logic to extract metadata parameters:
  - **Images**: width, height, and creation date.
  - **Audio**: artist, duration.
  - **PDFs**: pages count, author.
  - **Office Documents (docx, xlsx, pptx)**: pages count, author (natively parsed from properties).
- Integration of metadata extraction in background crawl task.
- GET endpoint `/file-metadata/{id}` returning metadata key-value pairs.

### Scoped Out / Deferred:
- OCR or text content extraction.
- Automatic thumbnail generation.
</domain>

<decisions>
## Implementation Decisions

### 1. Database Schema & Migration
- Add a new column `meta_data` (`String` / `VARCHAR` / `TEXT`) to the `FileRecord` model in `backend/database/models.py`.
- Implement self-healing migration in `create_tables()` inside `backend/database/init_db.py` to run `ALTER TABLE files ADD COLUMN meta_data TEXT` if the column does not already exist.

### 2. Extraction Libraries & Logic
- Use standard pure-Python libraries with no external binary requirements:
  - `pypdf` for PDF parsing.
  - `tinytag` for audio (MP3, WAV, etc.) parsing.
- Implement native parser for image dimensions (PNG, JPEG, GIF) to keep dependency footprint light.
- Implement native zip XML parser for Office document properties (creator and pages count).
- Handle all file read exceptions gracefully (silent logging) to ensure crawler never crashes on bad files.

### 3. API Endpoints
- Add a new HTTP GET endpoint `/file-metadata/{id}` in `backend/main.py`.
- It will load the `FileRecord` by ID, parse the `meta_data` string as JSON, and return it.

### 4. Background Crawl Integration
- Incorporate the metadata extraction service during background scans so that `meta_data` is saved to the database.
</decisions>

<canonical_refs>
## Canonical References

- [models.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/database/models.py) — Defines database schema.
- [init_db.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/database/init_db.py) — Handles database table creation.
- [file_service.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/services/file_service.py) — Manages database saving operations.
- [main.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/main.py) — FastAPI endpoints and background task manager.
</canonical_refs>
