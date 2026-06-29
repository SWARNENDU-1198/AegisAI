# Phase 4: Security Scan Engine - Research

## Regex Scan Patterns

We will search for secrets and PII using regex:
- **API Keys / Secrets**:
  - `(?i)(api[-_]?key|secret[-_]?key|private[-_]?key|token|auth[-_]?key)\s*[:=]\s*['"]([a-zA-Z0-9_\-]{16,})['"]`
- **Passwords**:
  - `(?i)(password|passwd)\s*[:=]\s*['"]([a-zA-Z0-9_\-]{8,})['"]`
- **SSN**:
  - `\b\d{3}-\d{2}-\d{4}\b`
- **Credit Card**:
  - `\b(?:\d{4}[ -]?){3}\d{4}\b`

## Safe Text File Reading
To prevent locking or crashing, files are scanned:
- Only if size < 1MB.
- Only for text-like extensions (`.txt`, `.md`, `.json`, `.yaml`, `.yml`, `.xml`, `.py`, `.js`, `.ts`, `.html`, `.css`, `.sh`, `.bat`, `.ps1`, `.ini`, `.env`).
- Decoded using `utf-8` with `errors="ignore"` parameter.

## Dangerous Extensions
Any file with the following extensions is flagged as `unverified_executable`:
- `.exe`, `.bat`, `.ps1`, `.vbs`, `.sh`, `.cmd`, `.msi`
- These are matched directly in the path/extension check.
