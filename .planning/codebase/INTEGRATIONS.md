# Integrations

**Analysis Date:** 2026-06-26

## External APIs

### Google Gemini API
- **Purpose**: Generates cleanup recommendations and answers user questions in natural language.
- **Model**: `gemini-2.5-flash`
- **Library**: `google-generativeai`
- **Credentials**: API Key loaded from `GEMINI_API_KEY` environment variable.
- **Integration Points**:
  - `backend/ai/gemini.py` - Wraps the initialization of the model and provides `ask_ai(prompt)` to send queries.
  - `backend/services/ai_service.py` - Generates custom prompt using storage analysis, largest files, and duplicate file metrics to retrieve cleanup recommendations.
  - `backend/services/chat_service.py` - Uses database storage metrics and files to answer natural language questions.

## Databases

### SQLite
- **Purpose**: Local relational database store for file metadata.
- **Database File**: `aegisai.db` in the workspace root (also references `backend/aegisai.db`).
- **Connection Details**: Initiated with SQLAlchemy `create_engine` using `sqlite:///aegisai.db`. Uses `check_same_thread=False` to allow FastAPI's multithreaded handlers.
- **Tables**:
  - `files` - Map of scanned file records, with schema details in `backend/database/models.py`.

## Configuration and Secrets

- **Environment File**: `.env` in the `backend/` directory.
- **Key Variables**:
  - `GEMINI_API_KEY` - API token for Google Generative AI authentication.
