# Milestones

## v1.0 MVP (Shipped: 2026-06-29)

**Phases completed:** 6 phases, 7 plans, 20 tasks

**Key accomplishments:**

- Optimized database insertions in `save_files` by loading all paths into a set and performing a single SQLAlchemy bulk_insert_mappings batch.
- Implemented non-blocking background crawler and hashing tasks using Python asyncio to keep the FastAPI event loop responsive while scanning large directories, including a new progress-tracking endpoint and concurrency locking.
- Implemented file categorization aggregates query and exposed the `/storage-by-category` GET endpoint.
- Implemented the Rich Metadata Engine to extract and store properties for images, audio, PDF, and Microsoft Office documents, and exposed a metadata retrieval endpoint.
- Implemented the Security Scan Engine to identify secrets, passwords, PII, and dangerous files, and exposed a security report endpoint.
- Implemented the Cleanup Control Engine with safe endpoints for user-confirmed duplicate deletion and temp file purges, and verified the functionality with unittests.
- Implemented the Semantic Search Engine & AI Summarizer to search documents using local embedding cosine similarities and generate conversational folder summaries.

---
