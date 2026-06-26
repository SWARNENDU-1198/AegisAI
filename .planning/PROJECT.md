# AegisAI

## What This Is

AegisAI is an AI-powered Digital Intelligence Platform that understands, organizes, secures, and optimizes a user's computer. It is not a file cleaner; rather, it acts as an intelligent operating layer for Windows that understands the user's digital life.

## Core Value

Provides a safe, intelligent digital assistant that helps users understand, search, and optimize their local machine's files, storage, and security without automated destructive changes.

## Requirements

### Validated

- [x] **File Scanning** - Recursively crawls specific local directories (`SCAN_PATHS`) to index files and directories.
- [x] **File Hashing** - Generates SHA-256 signatures for scanned files to identify uniqueness.
- [x] **File Database Persistence** - Saves indexed file metadata (name, path, size, extension, hash) to a local SQLite database.
- [x] **Storage Analysis** - Computes general disk metrics including total file count, total size, and average file size.
- [x] **Largest Files Detection** - Identifies and lists the top N largest files on the disk.
- [x] **Duplicate Files Detection** - Identifies groups of duplicate files by comparing SHA-256 signatures.
- [x] **AI Cleanup Advice** - Analyzes storage metrics, largest files, and duplicate groups to give tailored recommendations using Google Gemini.
- [x] **AI Chat Bot** - Allows users to ask natural-language questions about their files and storage context.

### Active

- [ ] **Database Optimization** - Eliminate the N+1 query bottleneck in `file_service.py` during bulk file indexing.
- [ ] **Async Scanning & Hashing** - Convert synchronous file operations and crawling into non-blocking background tasks to keep the FastAPI server responsive.
- [ ] **File Categorization Engine** - Intelligently group scanned files into specific logical types (e.g., Media, Documents, Archives, Code) based on suffix or MIME-type.
- [ ] **Metadata Engine** - Extract rich metadata from common file types (e.g., dimension for images, duration for audio, author for documents).
- [ ] **Suspicious & Sensitive File Detection** - Scan files for security risks (malicious scripts) or plain-text sensitive info (keys, passwords, PII).
- [ ] **Cleanup Engine** - Provide a mechanism for users to review and safely execute storage recovery actions (e.g., deleting selected duplicates).

### Out of Scope

- **Automated File Deletion** - AegisAI must never delete files automatically; all destructive actions require explicit user confirmation to prevent data loss.
- **Direct Cloud Sync Management** - Managing external cloud storage accounts is excluded from the initial scope to focus on local storage.

## Context

- The current implementation is a Python FastAPI web server that talks to a local SQLite file (`aegisai.db`).
- Integrates with the Google Gemini API using the `google-generativeai` SDK.
- The default directories to scan are configured in `backend/config.py` targeting Windows user directories (Desktop, Documents, Downloads, Pictures, Videos).

## Constraints

- **Operating System**: Windows - Tailored for Windows file directories and structures.
- **Tech Stack**: Python (3.14.3), FastAPI, SQLAlchemy, SQLite, and Google Gemini.
- **Security & Data Safety**: All AI recommendations are advisory; destructive actions must be user-validated.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| SQLite for Database | Simple, zero-configuration local database matching the local app vision | ✔ Good |
| Gemini 2.5 Flash | Fast, low-latency, and cost-effective AI model for natural language requests | ✔ Good |
| No Automatic Deletions | Guarantees user trust and prevents accidental data loss during system cleanup | ✔ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? ➔ Move to Out of Scope with reason
2. Requirements validated? ➔ Move to Validated with phase reference
3. New requirements emerged? ➔ Add to Active
4. Decisions to log? ➔ Add to Key Decisions
5. "What This Is" still accurate? ➔ Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check ➔ still the right priority?
3. Audit Out of Scope ➔ reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-26 after initialization*
