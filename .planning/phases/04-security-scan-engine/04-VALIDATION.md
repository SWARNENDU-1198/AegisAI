# Phase 4: Security Scan Engine - Validation

## Testing Plan

We will create a test suite `backend/test_security.py` containing:

1. **Unit Tests for Secrets Scanner**:
   - Check file content with mock API Key matches.
   - Check file content with mock Password matches.
   - Check file content with mock SSN/Credit Card matches.
   - Verify files without secrets do not trigger warnings.

2. **Unit Tests for Dangerous Files Scanner**:
   - Verify flagging of `.exe`, `.bat`, `.ps1` extensions.
   - Verify ignoring of safe extensions.

3. **Integration Tests**:
   - Verify background scanning identifies and logs security alerts in `meta_data` field.
   - Verify `/security-report` endpoint returns the grouped list of alerts correctly.
