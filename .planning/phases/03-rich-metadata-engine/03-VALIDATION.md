# Phase 3: Rich Metadata Engine - Validation

## Testing Plan

We will create a test suite `backend/test_metadata.py` covering:

1. **Unit Tests for Native Image Parsing**:
   - Verify width/height extraction for mock PNG files.
   - Verify width/height extraction for mock JPEG files.
   - Verify width/height extraction for mock GIF files.
   - Verify creation date formatting.

2. **Unit Tests for PDF and Office XML Parsing**:
   - Verify PDF page counting and author metadata via a simulated or actual PDF.
   - Verify DOCX/PPTX creator and pages parsing from zip containers.

3. **Unit Tests for Audio Parsing**:
   - Verify duration and artist reading from mock/loaded MP3 structures.

4. **Integration Tests**:
   - Verify background scanning processes files, extracts metadata, and saves them to SQLite.
   - Verify GET `/file-metadata/{id}` endpoint loads records and correctly parses/returns the `meta_data` dictionary.

## Verification Commands

Run the metadata test suite:
```bash
venv\Scripts\python.exe -m unittest backend/test_metadata.py
```
