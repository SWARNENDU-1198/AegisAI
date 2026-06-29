# Phase 6: Semantic Search & AI Summaries - Context

**Gathered:** 2026-06-26
**Status:** Ready for planning
**Source:** Autonomous Phase Initialization

<domain>
## Phase Boundary

This phase implements semantic search and AI-powered directory summaries in AegisAI. It delivers embedding storage in the database, a semantic search endpoint, and a directory summarizer calling Google Gemini.

### Scoped In:
- Schema modification to add a `vector_embedding` column (`String` / `TEXT` / `BLOB`) to `FileRecord` to store the serialized vector embedding.
- Generating embeddings for files during indexing using the Google Gemini text embedding API (`models/text-embedding-004`).
- Custom pure-Python cosine similarity calculator to match search query embeddings against database records.
- GET endpoint `/semantic-search` returning top matches.
- GET endpoint `/folder-summary` summarizing folder contents (list of files, sizes, categories, security alerts) using Gemini LLM.

### Scoped Out / Deferred:
- Heavy local vector database engines (Milvus, Qdrant) due to package dependency footprint.
- Large local embedding model downloads (sentence-transformers).
</domain>

<decisions>
## Implementation Decisions

### 1. Database Schema & Migration
- Add `vector_embedding` (`TEXT` or `BLOB`) column to `FileRecord` in `backend/database/models.py`.
- Implement self-healing migration in `create_tables()` inside `backend/database/init_db.py` to run `ALTER TABLE files ADD COLUMN vector_embedding TEXT` if missing.

### 2. Embeddings & Search
- Compute file text representations for embedding:
  `"Name: {name} | Category: {category} | Extension: {extension} | Metadata: {meta_data}"`
- Send this string to the Gemini Embedding API (`models/text-embedding-004`) to get a 768-dimensional float vector.
- Serialize the float list to a JSON string or float list to save in the `vector_embedding` column.
- On query `/semantic-search?q=...`, fetch the query embedding from Gemini, retrieve all file records with embeddings from DB, compute cosine similarity natively in Python, and return the top N matches.

### 3. Folder Summaries
- GET `/folder-summary?path=...` queries the database for all files starting with or nested under the specified directory path.
- Formulate a prompt compiling file counts, sizes, categories, metadata, and security findings.
- Call Gemini generative API to summarize: *"Tell the user what this folder is about, its key contents, any security concerns, and general optimization suggestions."*
</decisions>

<canonical_refs>
## Canonical References

- [models.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/database/models.py) — Defines schema.
- [init_db.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/database/init_db.py) — Table creation and migrations.
- [main.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/main.py) — API endpoints.
- [gemini.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/ai/gemini.py) — Gemini API wrapper.
</canonical_refs>
