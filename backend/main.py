from fastapi import FastAPI

try:
    from config import SCAN_PATHS
except ImportError:
    from backend.config import SCAN_PATHS

try:
    from scanner.scanner import scan_multiple_directories
except ImportError:
    from backend.scanner.scanner import scan_multiple_directories

try:
    from database.init_db import create_tables
except ImportError:
    from backend.database.init_db import create_tables

try:
    from services.hash_service import calculate_hash
except ImportError:
    from backend.services.hash_service import calculate_hash

try:
    from services.file_service import save_files
except ImportError:
    from backend.services.file_service import save_files

try:
    from services.duplicate_service import find_duplicates
except ImportError:
    from backend.services.duplicate_service import find_duplicates


app = FastAPI(
    title="AegisAI",
    description="AI File Intelligence System",
    version="1.0"
)

# Create database tables automatically
create_tables()


@app.get("/")
def home():
    return {
        "message": "AegisAI Running"
    }


@app.get("/scan")
def scan():

    files = scan_multiple_directories(SCAN_PATHS)

    return {
        "count": len(files),
        "files": files[:50]
    }


@app.get("/scan-and-save")
def scan_and_save():

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