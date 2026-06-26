# Roadmap

## Proposed Roadmap

**5 phases** | **11 requirements mapped** | All active requirements covered ✔

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Database & Crawler Optimization | Eliminate DB insertion loops and run disk crawls asynchronously | CORE-05, CORE-06 | 3 |
| 2 | File Categorization Engine | Group scanned files into logical categories (Media, Docs, etc.) | CAT-01, CAT-02 | 2 |
| 3 | Rich Metadata Engine | Parse specific details (dimensions, duration, author) from file types | META-01, META-02, META-03 | 2 |
| 4 | Security Scan Engine | Detect plaintext sensitive information and suspicious script files | SEC-01, SEC-02 | 2 |
| 5 | Cleanup Control Engine | Enable safe user-confirmed file deletion to recover disk storage | CLEAN-01, CLEAN-02 | 2 |

---

### Phase Details

**Phase 1: Database & Crawler Optimization**
- **Goal**: Optimize indexing performance and convert file scanning and hashing into non-blocking background processes.
- **Requirements**: `CORE-05`, `CORE-06`
- **Success Criteria**:
  1. API request `/scan-and-save` returns a task ID immediately and does not block the FastAPI event loop.
  2. Database saves are refactored into a single optimized query or batch execution, resolving the N+1 SELECT loops.
  3. Status endpoint `/scan-status/{task_id}` correctly tracks scan progress.

**Phase 2: File Categorization Engine**
- **Goal**: Classify indexed files by file extension or structure into logical groups.
- **Requirements**: `CAT-01`, `CAT-02`
- **Success Criteria**:
  1. File records schema is updated to track categories, or dynamic indexing classifications are implemented.
  2. Endpoint `/storage-by-category` returns total file counts and cumulative byte sizes for each category.

**Phase 3: Rich Metadata Engine**
- **Goal**: Extract details from media and document file formats.
- **Requirements**: `META-01`, `META-02`, `META-03`
- **Success Criteria**:
  1. Extractor module extracts width/height for images, duration/artist for MP3s, and pages/author for PDFs.
  2. `/file-metadata/{id}` retrieves the extracted metadata parameters.

**Phase 4: Security Scan Engine**
- **Goal**: Identify insecure files or scripts and find leaked secrets like API keys or passwords.
- **Requirements**: `SEC-01`, `SEC-02`
- **Success Criteria**:
  1. Regex scanner identifies plaintext API keys, passwords, and PII patterns in text documents.
  2. Scanner alerts users to potentially dangerous file types (e.g. unverified `.exe`, `.bat`, `.ps1` in user spaces).

**Phase 5: Cleanup Control Engine**
- **Goal**: Implement user-triggered deletions for duplicates and junk files.
- **Requirements**: `CLEAN-01`, `CLEAN-02`
- **Success Criteria**:
  1. Endpoint `/delete-duplicate` accepts target file path and duplicate hash, executing deletion only with explicit confirmation parameters.
  2. Database reflects deletions immediately and updates disk space metrics.
