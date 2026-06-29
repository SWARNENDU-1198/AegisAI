# Phase 4: Security Scan Engine - Context

**Gathered:** 2026-06-26
**Status:** Ready for planning
**Source:** Autonomous Phase Initialization

<domain>
## Phase Boundary

This phase implements a security scanner for AegisAI. It identifies plain-text sensitive info (keys, passwords, PII) in text-like documents and warns about dangerous script/executable extensions in user spaces.

### Scoped In:
- Logic to scan text files for plain-text sensitive patterns:
  - API Keys / Secret Tokens: `(?i)(api[-_]?key|secret[-_]?key|private[-_]?key|token)\s*[:=]\s*['"][a-zA-Z0-9_\-]{16,}['"]`
  - Passwords: `(?i)(password|passwd)\s*[:=]\s*['"][a-zA-Z0-9_\-]{8,}['"]`
  - PII (SSN): `\b\d{3}-\d{2}-\d{4}\b`
  - PII (Credit Card): `\b(?:\d{4}[ -]?){3}\d{4}\b`
- Identification of unverified executable/script files:
  - Extensions: `.exe`, `.bat`, `.ps1`, `.vbs`, `.sh`, `.cmd`, `.msi`
- Integrating security analysis into background scans and merging findings into the file's JSON `meta_data` field.
- GET endpoint `/security-report` listing all files with security findings.

### Scoped Out / Deferred:
- Static binary analysis or malware signature matching.
- Real-time network security scanning.
</domain>

<decisions>
## Implementation Decisions

### 1. Storage of Security Findings
- Save findings under the `meta_data` column as a JSON key:
  `{"security_alerts": ["contains_api_key", "contains_password", "unverified_executable"]}`
- This avoids schema modifications and keeps file metadata self-contained.

### 2. File Reading Safety
- Limits scanning to files under 1MB to prevent performance bottlenecks.
- Reads files in text mode, skipping binary decode errors.
- Handles file read/access permission exceptions gracefully.

### 3. API Endpoints
- Expose `/security-report` which queries all `FileRecord`s, checks for `security_alerts` in `meta_data`, and returns them grouped by warning type.
</decisions>

<canonical_refs>
## Canonical References

- [main.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/main.py) — API endpoints and scan tasks.
- [metadata_service.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/services/metadata_service.py) — Metadata dispatcher.
- [security_service.py](file:///c:/Users/dmukh/OneDrive/Desktop/AegisAI/backend/services/security_service.py) [NEW] — Security analysis logic.
</canonical_refs>
