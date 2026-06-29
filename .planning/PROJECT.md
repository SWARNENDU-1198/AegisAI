# AegisAI

## What This Is

AegisAI is an AI-powered Digital Intelligence Platform that understands, organizes, secures, and optimizes a user's computer. It acts as an intelligent operating layer for Windows that understands the user's digital life.

## Core Value

Provides a safe, intelligent digital assistant that helps users understand, search, and optimize their local machine's files, storage, and security without automated destructive changes.

## Current State (Shipped v1.0 MVP)

AegisAI has completed its v1.0 MVP milestone. The following capabilities are fully implemented, verified, and operational:
- **Asynchronous Hashing Crawler:** Non-blocking filesystem scanner with set-based insertion logic to prevent N+1 query loops.
- **Multi-Category Parser:** Extension-based and file signature-based categorization (Media, Documents, Code, Archives, Temp).
- **Rich Metadata Extraction:** File property parsers for images, audio tags (tinytag), PDFs (pypdf), and Microsoft Office XML.
- **Regex Security Scanner:** Automatic alerts for dangerous file types and credentials (API keys, passwords, SSN, Credit Cards) stored in metadata.
- **Cleanup Actions:** Safe endpoints for deleting duplicates and temp files with mandatory user confirmation guards.
- **Semantic search & LLM Summarizer:** Conversational query vector generation using `models/gemini-embedding-001` and interactive directory reviews using Google Gemini.

## Requirements

### Validated

- [x] **File Scanning** - Recursively crawls specific local directories (`SCAN_PATHS`) to index files and directories. (shipped v1.0)
- [x] **File Hashing** - Generates SHA-256 signatures for scanned files to identify uniqueness. (shipped v1.0)
- [x] **File Database Persistence** - Saves indexed file metadata (name, path, size, extension, hash) to a local SQLite database. (shipped v1.0)
- [x] **Storage Analysis** - Computes general disk metrics including total file count, total size, and average file size. (shipped v1.0)
- [x] **Largest Files Detection** - Identifies and lists the top N largest files on the disk. (shipped v1.0)
- [x] **Duplicate Files Detection** - Identifies groups of duplicate files by comparing SHA-256 signatures. (shipped v1.0)
- [x] **AI Cleanup Advice** - Analyzes storage metrics, largest files, and duplicate groups to give recommendations. (shipped v1.0)
- [x] **AI Chat Bot** - Allows users to ask natural-language questions about their files and storage context. (shipped v1.0)
- [x] **Database Optimization** - Eliminate the N+1 query bottleneck in `file_service.py` during bulk file indexing. (shipped v1.0)
- [x] **Async Scanning & Hashing** - Convert synchronous file operations and crawling into non-blocking background tasks. (shipped v1.0)
- [x] **File Categorization Engine** - Intelligently group scanned files into specific logical types. (shipped v1.0)
- [x] **Metadata Engine** - Extract rich metadata from common file formats (Images, Audio, PDF, Office XML). (shipped v1.0)
- [x] **Suspicious & Sensitive File Detection** - Scan files for security risks or plain-text credentials. (shipped v1.0)
- [x] **Cleanup Engine** - Safe mechanism for users to delete selected duplicates and temporary files. (shipped v1.0)
- [x] **Semantic Search & AI Summaries** - Search files using local embedding cosine similarities and summarize folder hierarchies. (shipped v1.0)

### Active

- [ ] **CLI interface** - A simple command-line interface to invoke background scans and query database stats without using external API clients. (Planned for next iteration)
- [ ] **Embedding Rate-Limiter** - Implement backoff and retries for the Gemini embedding engine to prevent 429 errors during huge crawls. (Planned for next iteration)

### Out of Scope

- **Automated File Deletion** - AegisAI must never delete files automatically; all destructive actions require explicit user confirmation to prevent data loss.
- **Direct Cloud Sync Management** - Managing external cloud storage accounts is excluded to focus on local storage.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| SQLite for Database | Simple, zero-configuration local database matching the local app vision | ✔ Good |
| Gemini 2.5 Flash | Fast, low-latency, and cost-effective AI model for natural language requests | ✔ Good |
| No Automatic Deletions | Guarantees user trust and prevents accidental data loss during system cleanup | ✔ Good |
| Standardized DB Path | Resolved path dynamically relative to the module file to prevent database split bugs | ✔ Good |
| gemini-embedding-001 | Stable embedding model supported by the workspace developer API key | ✔ Good |

---
*Last updated: 2026-06-29 after v1.0 milestone completion*
