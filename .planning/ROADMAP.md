# Roadmap: AegisAI

## Milestones

- 🚧 **v1.0 MVP** - Phases 1-5 (in progress)

## Phases

- [x] **Phase 1: Database & Crawler Optimization** - Optimize indexing performance and convert file scanning and hashing into non-blocking background processes. (completed 2026-06-26)
- [ ] **Phase 2: File Categorization Engine** - Classify indexed files by file extension or structure into logical groups.
- [ ] **Phase 3: Rich Metadata Engine** - Extract details from media and document file formats.
- [ ] **Phase 4: Security Scan Engine** - Identify insecure files or scripts and find leaked secrets.
- [ ] **Phase 5: Cleanup Control Engine** - Implement user-triggered deletions for duplicates and junk files.

## Phase Details

### Phase 1: Database & Crawler Optimization
**Goal**: Optimize indexing performance and convert file scanning and hashing into non-blocking background processes.
**Depends on**: Nothing
**Requirements**: CORE-05, CORE-06
**Success Criteria** (what must be TRUE):
  1. API request `/scan-and-save` returns a task ID immediately and does not block the FastAPI event loop.
  2. Database saves are refactored into a single optimized query or batch execution, resolving the N+1 SELECT loops.
  3. Status endpoint `/scan-status/{task_id}` correctly tracks scan progress.
**Plans**: TBD

Plans:
- [x] 01-01: Optimize database indexing queries
- [x] 01-02: Implement asynchronous background disk scans and hashing tasks

### Phase 2: File Categorization Engine
**Goal**: Classify indexed files by file extension or structure into logical groups.
**Depends on**: Phase 1
**Requirements**: CAT-01, CAT-02
**Success Criteria** (what must be TRUE):
  1. File records schema is updated to track categories, or dynamic indexing classifications are implemented.
  2. Endpoint `/storage-by-category` returns total file counts and cumulative byte sizes for each category.
**Plans**: TBD

### Phase 3: Rich Metadata Engine
**Goal**: Extract details from media and document file formats.
**Depends on**: Phase 2
**Requirements**: META-01, META-02, META-03
**Success Criteria** (what must be TRUE):
  1. Extractor module extracts width/height for images, duration/artist for MP3s, and pages/author for PDFs.
  2. `/file-metadata/{id}` retrieves the extracted metadata parameters.
**Plans**: TBD

### Phase 4: Security Scan Engine
**Goal**: Identify insecure files or scripts and find leaked secrets like API keys or passwords.
**Depends on**: Phase 3
**Requirements**: SEC-01, SEC-02
**Success Criteria** (what must be TRUE):
  1. Regex scanner identifies plaintext API keys, passwords, and PII patterns in text documents.
  2. Scanner alerts users to potentially dangerous file types (e.g. unverified `.exe`, `.bat`, `.ps1` in user spaces).
**Plans**: TBD

### Phase 5: Cleanup Control Engine
**Goal**: Implement user-triggered deletions for duplicates and junk files.
**Depends on**: Phase 4
**Requirements**: CLEAN-01, CLEAN-02
**Success Criteria** (what must be TRUE):
  1. Endpoint `/delete-duplicate` accepts target file path and duplicate hash, executing deletion only with explicit confirmation parameters.
  2. Database reflects deletions immediately and updates disk space metrics.
**Plans**: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1     | v1.0      | 2/2 | Complete   | 2026-06-26 |
| 2     | v1.0      | 0/0            | Not started | - |
| 3     | v1.0      | 0/0            | Not started | - |
| 4     | v1.0      | 0/0            | Not started | - |
| 5     | v1.0      | 0/0            | Not started | - |
