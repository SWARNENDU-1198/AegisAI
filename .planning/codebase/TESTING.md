# Testing Patterns

**Analysis Date:** 2026-06-26

## Test Framework

- **Automated Testing**: There is currently no automated test runner (such as `pytest` or `unittest`) installed or configured in the Python environment.
- **Assertion Library**: No formal assertion library is implemented.

## Existing Test Scripts

There are no formal test suites. Instead, verification is done via manual/integration scripts:

### AI Connectivity Script (`backend/test_ai.py`)
- **Purpose**: Verifies that the Google Generative AI integration is configured and authenticated correctly.
- **Execution Command**:
  ```bash
  python backend/test_ai.py
  ```
- **Code Structure**:
  ```python
  from ai.gemini import ask_ai

  print(ask_ai("Say hello from AegisAI."))
  ```

## Manual Endpoint Verification

Manual endpoint testing can be done by starting the FastAPI server and accessing the Swagger UI:

- **Launch Command**:
  ```bash
  uvicorn main:app --reload
  ```
- **Documentation Endpoint**: `http://localhost:8000/docs` (interactive Swagger UI to test routes manually).
