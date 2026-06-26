# Technology Stack

**Analysis Date:** 2026-06-26

## Languages and Runtimes

- **Python**: 3.14.3 (runs in `venv` virtual environment)

## Backend Framework

- **FastAPI**: 0.136.3 (used for Web API routing and application server)
- **Uvicorn**: 0.49.0 (ASGI web server implementation)

## Database and ORM

- **SQLite**: Built-in Python database, stores file records locally in `aegisai.db`
- **SQLAlchemy**: 2.0.50 (Object Relational Mapper for database modeling and queries)

## AI Libraries

- **Google Generative AI (`google-generativeai`)**: 0.8.6 (used to communicate with Google Gemini API)

## Other Core Dependencies

- **Pydantic**: 2.13.4 (data validation and settings management using python type annotations)
- **python-dotenv**: 1.2.2 (reads key-value pairs from a `.env` file and sets them as environment variables)
