from fastapi import FastAPI

# Config
try:
    from config import SCAN_PATHS
except ImportError:
    SCAN_PATHS = []
    print("[WARNING] config.py not found")


# Scanner
try:
    from scanner.scanner import scan_multiple_directories
except ImportError:
    scan_multiple_directories = None
    print("[WARNING] scanner module not found")


# Database
try:
    from database.init_db import create_tables
except ImportError:
    create_tables = None
    print("[WARNING] database init module not found")


# Services
try:
    from services.hash_service import calculate_hash
except ImportError:
    calculate_hash = None
    print("[WARNING] hash service not found")


try:
    from services.file_service import save_files
except ImportError:
    save_files = None
    print("[WARNING] file service not found")


try:
    from services.duplicate_service import find_duplicates
except ImportError:
    find_duplicates = None
    print("[WARNING] duplicate service not found")


try:
    from services.storage_service import (
        get_storage_analysis,
        get_largest_files
    )
except ImportError:
    get_storage_analysis = None
    get_largest_files = None
    print("[WARNING] storage service not found")


try:
    from services.ai_service import (
        generate_cleanup_advice
    )
except ImportError:
    generate_cleanup_advice = None
    print("[WARNING] ai service not found")


try:
    from services.chat_service import (
        answer_question
    )
except ImportError:
    answer_question = None
    print("[WARNING] chat service not found")


# Chat Models
try:
    from models.chat_models import (
        ChatRequest
    )
except ImportError:
    ChatRequest = None
    print("[WARNING] chat models not found")


app = FastAPI(
    title="AegisAI",
    description="AI Powered Digital Intelligence Platform",
    version="1.0"
)


# Initialize Database
if create_tables:
    create_tables()


@app.get("/")
def home():
    return {
        "message": "AegisAI Running"
    }


@app.get("/scan")
def scan():

    if not scan_multiple_directories:
        return {
            "error": "Scanner module not loaded"
        }

    files = scan_multiple_directories(SCAN_PATHS)

    return {
        "count": len(files),
        "files": files[:50]
    }


@app.get("/scan-and-save")
def scan_and_save():

    if not scan_multiple_directories:
        return {
            "error": "Scanner module not loaded"
        }

    if not calculate_hash:
        return {
            "error": "Hash service not loaded"
        }

    if not save_files:
        return {
            "error": "File service not loaded"
        }

    files = scan_multiple_directories(SCAN_PATHS)

    for file in files:
        file["hash"] = calculate_hash(file["path"])

    save_files(files)

    return {
        "message": "Files scanned and saved successfully",
        "count": len(files)
    }


@app.get("/duplicates")
def duplicates():

    if not find_duplicates:
        return {
            "error": "Duplicate service not loaded"
        }

    duplicate_files = find_duplicates()

    total_duplicate_files = 0
    recoverable_space = 0

    for group in duplicate_files:

        total_duplicate_files += group["count"]

        if group["count"] > 1:
            recoverable_space += (
                group["count"] - 1
            ) * group["files"][0]["size"]

    return {
        "duplicate_groups": len(duplicate_files),
        "duplicate_files": total_duplicate_files,
        "recoverable_space_bytes": recoverable_space,
        "duplicates": duplicate_files
    }


@app.get("/storage-analysis")
def storage_analysis():

    if not get_storage_analysis:
        return {
            "error": "Storage service not loaded"
        }

    return get_storage_analysis()


@app.get("/largest-files")
def largest_files():

    if not get_largest_files:
        return {
            "error": "Storage service not loaded"
        }

    return {
        "largest_files": get_largest_files()
    }


@app.get("/ai-cleanup-advice")
def ai_cleanup_advice():

    if not generate_cleanup_advice:
        return {
            "error": "AI Service not loaded"
        }

    return {
        "advice": generate_cleanup_advice()
    }


@app.post("/chat")
def chat(request: ChatRequest):

    if not answer_question:
        return {
            "error": "Chat service not loaded"
        }

    return {
        "answer": answer_question(
            request.question
        )
    }