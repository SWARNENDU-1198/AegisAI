# Phase 2: File Categorization Engine - Context

**Gathered:** 2026-06-26
**Status:** Ready for planning
**Source:** Autonomous Phase Initialization

<domain>
## Phase Boundary

This phase implements file categorization capabilities within AegisAI to group files into logical domains. It delivers schema changes, crawler indexing integration, and a storage-by-category stats endpoint.

### Scoped In:
- Schema modification of the `files` table to include a `category` column.
- Logic to automatically map file extensions and/or file structures (magic bytes) to logical categories: `Media`, `Documents`, `Code`, `Archives`, `Temp`, and `Other`.
- Automatic schema migration check during database initialization to safely add the `category` column to the SQLite database.
- Integration of categorization logic into the background crawl scanner so that files are categorized during discovery.
- Exposing a `/storage-by-category` GET endpoint returning count and size aggregations.

### Scoped Out / Deferred:
- Semantic classification using LLM text embeddings (deferred to Phase 5).
- Real-time file system watchers (deferred to Phase 3).
</domain>

<decisions>
## Implementation Decisions

### 1. Database Schema & Migration
- Add a new column `category` (`String` / `VARCHAR`) to the `FileRecord` model in `backend/database/models.py`.
- Implement self-healing migration in `create_tables()` inside `backend/database/init_db.py` to run `ALTER TABLE files ADD COLUMN category VARCHAR` if the column does not already exist.

### 2. Categorization Rules
- Map extensions to categories:
  - **Media**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.mp3`, `.wav`, `.mp4`, `.mkv`, `.avi`, `.mov`, `.flac`, `.ogg`, `.webm`, `.svg`, `.ico`, `.tiff`, `.webp`
  - **Documents**: `.pdf`, `.docx`, `.doc`, `.xlsx`, `.xls`, `.pptx`, `.ppt`, `.txt`, `.rtf`, `.odt`, `.csv`, `.md`
  - **Code**: `.py`, `.js`, `.ts`, `.html`, `.css`, `.json`, `.java`, `.c`, `.cpp`, `.h`, `.cs`, `.go`, `.rs`, `.php`, `.rb`, `.sh`, `.bat`, `.ps1`, `.xml`, `.yaml`, `.yml`, `.sql`
  - **Archives**: `.zip`, `.tar`, `.gz`, `.rar`, `.7z`, `.bz2`, `.tgz`
  - **Temp**: `.tmp`, `.temp`, `.bak`, `.log`, `.cache`
- Fallback to reading file signatures (magic bytes) for files with unknown/empty extensions up to the first 8 bytes.
- Return `"Other"` if no match is found.

### 3. API endpoints
- Add a new HTTP GET endpoint `/storage-by-category` in `backend/main.py`.
- It will execute a single SQLAlchemy aggregate query (`GROUP BY category`) to pull counts and total size per category, returning a JSON response.
- Example response:
  ```json
  {
    "Media": { "count": 142, "total_size_bytes": 48293902 },
    "Documents": { "count": 89, "total_size_bytes": 1283991 }
  }
  ```

### 4. Background Crawl Integration
- Incorporate the categorization service during background scans so that `category` is saved to the database along with names, paths, hashes, and sizes.
</decisions>

<canonical_refs>
## Canonical References

- [models.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/database/models.py) — Defines database schema.
- [init_db.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/database/init_db.py) — Handles database table creation.
- [file_service.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/services/file_service.py) — Manages database saving operations.
- [main.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/main.py) — FastAPI endpoints and background task manager.
</canonical_refs>

<specifics>
## Specific Ideas
- To keep the crawling and hashing process fast, file structure checking (reading magic bytes) must only be triggered as a fallback if the file extension is empty or not mapped.
</specifics>

<deferred>
## Deferred Ideas
- Dynamic machine-learning based file category clustering (deferred to later phases).
</deferred>
