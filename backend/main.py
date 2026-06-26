import asyncio
import logging
import threading
import time
import uuid
from fastapi import FastAPI, HTTPException, status

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Config
try:
    from config import SCAN_PATHS
except ImportError:
    SCAN_PATHS = []
    logger.warning("config.py not found")


# Scanner
try:
    from scanner.scanner import scan_multiple_directories
except ImportError:
    scan_multiple_directories = None
    logger.warning("scanner module not found")


# Database
try:
    from database.init_db import create_tables
except ImportError:
    create_tables = None
    logger.warning("database init module not found")


# Services
try:
    from services.hash_service import calculate_hash
except ImportError:
    calculate_hash = None
    logger.warning("hash service not found")


try:
    from services.file_service import save_files
except ImportError:
    save_files = None
    logger.warning("file service not found")


try:
    from services.duplicate_service import find_duplicates
except ImportError:
    find_duplicates = None
    logger.warning("duplicate service not found")


try:
    from services.storage_service import (
        get_storage_analysis,
        get_largest_files
    )
except ImportError:
    get_storage_analysis = None
    get_largest_files = None
    logger.warning("storage service not found")


try:
    from services.ai_service import (
        generate_cleanup_advice
    )
except ImportError:
    generate_cleanup_advice = None
    logger.warning("ai service not found")


try:
    from services.chat_service import (
        answer_question
    )
except ImportError:
    answer_question = None
    logger.warning("chat service not found")


# Chat Models
try:
    from models.chat_models import (
        ChatRequest
    )
except ImportError:
    ChatRequest = None
    logger.warning("chat models not found")


app = FastAPI(
    title="AegisAI",
    description="AI Powered Digital Intelligence Platform",
    version="1.0"
)


# Initialize Database
if create_tables:
    create_tables()


# Global state to track background scanning
scan_state = {
    "task_id": None,
    "status": "idle",  # "idle", "running", "completed", "failed"
    "total_files": 0,
    "processed_files": 0,
    "current_file": None,
    "error": None,
    "start_time": None,
    "end_time": None,
    "elapsed_seconds": 0
}
scan_lock = threading.Lock()


async def background_scan_task(task_id: str) -> None:
    """Run filesystem scanning and hashing in background thread pools."""
    global scan_state
    logger.info("Background scan task %s started", task_id)
    start_epoch = time.time()
    
    try:
        if not scan_multiple_directories or not calculate_hash or not save_files:
            raise RuntimeError("Required scanner or persistence services are not loaded")

        # Step 1: Scan directories using asyncio.to_thread to keep main loop responsive
        logger.info("Executing filesystem crawl in background thread...")
        files = await asyncio.to_thread(scan_multiple_directories, SCAN_PATHS)
        
        total_count = len(files)
        with scan_lock:
            if scan_state["task_id"] != task_id:
                logger.warning("Task %s was superseded or cancelled", task_id)
                return
            scan_state["total_files"] = total_count
            scan_state["processed_files"] = 0
            
        logger.info("Crawl completed. Found %d files. Hashing and verifying...", total_count)
        
        # Step 2: Hashing files one-by-one, yielding control to main loop
        for idx, file in enumerate(files):
            with scan_lock:
                if scan_state["task_id"] != task_id:
                    logger.warning("Task %s was cancelled during hashing", task_id)
                    return
            
            # Hashing is CPU-bound; run in a threadpool worker
            file_hash = await asyncio.to_thread(calculate_hash, file["path"])
            file["hash"] = file_hash
            
            # Update state progress
            with scan_lock:
                scan_state["processed_files"] = idx + 1
                scan_state["current_file"] = file["path"]
                scan_state["elapsed_seconds"] = int(time.time() - start_epoch)
        
        # Step 3: Persistence
        logger.info("Hashed all files. Bulk persisting %d records to SQLite...", total_count)
        await asyncio.to_thread(save_files, files)
        
        # Mark completed
        with scan_lock:
            if scan_state["task_id"] == task_id:
                scan_state["status"] = "completed"
                scan_state["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                scan_state["elapsed_seconds"] = int(time.time() - start_epoch)
                scan_state["current_file"] = None
        logger.info("Background scan task %s successfully finished", task_id)
        
    except Exception as e:
        logger.exception("Error in background scan task %s: %s", task_id, str(e))
        with scan_lock:
            if scan_state["task_id"] == task_id:
                scan_state["status"] = "failed"
                scan_state["error"] = str(e)
                scan_state["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                scan_state["elapsed_seconds"] = int(time.time() - start_epoch)


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
async def scan_and_save():
    global scan_state
    
    if not scan_multiple_directories:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scanner module not loaded"
        )
    if not calculate_hash:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Hash service not loaded"
        )
    if not save_files:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="File service not loaded"
        )
        
    with scan_lock:
        if scan_state["status"] == "running":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "Scan already in progress",
                    "task_id": scan_state["task_id"],
                    "processed_files": scan_state["processed_files"],
                    "total_files": scan_state["total_files"]
                }
            )
            
        task_id = str(uuid.uuid4())
        scan_state.update({
            "task_id": task_id,
            "status": "running",
            "total_files": 0,
            "processed_files": 0,
            "current_file": None,
            "error": None,
            "start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "end_time": None,
            "elapsed_seconds": 0
        })
        
    asyncio.create_task(background_scan_task(task_id))
    
    return {
        "message": "Scan started in background",
        "task_id": task_id
    }


@app.get("/scan-status/{task_id}")
def scan_status(task_id: str):
    global scan_state
    
    with scan_lock:
        if scan_state["task_id"] != task_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
            
        total = scan_state["total_files"]
        processed = scan_state["processed_files"]
        progress_percent = int((processed / total) * 100) if total > 0 else 0
        
        return {
            "task_id": scan_state["task_id"],
            "status": scan_state["status"],
            "total_files": total,
            "processed_files": processed,
            "progress_percent": progress_percent,
            "current_file": scan_state["current_file"],
            "error": scan_state["error"],
            "start_time": scan_state["start_time"],
            "end_time": scan_state["end_time"],
            "elapsed_seconds": scan_state["elapsed_seconds"]
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