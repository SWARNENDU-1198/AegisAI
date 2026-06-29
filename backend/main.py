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


try:
    from database.db import SessionLocal
    from database.models import FileRecord
except ImportError:
    SessionLocal = None
    FileRecord = None
    logger.warning("database db or models not found")



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
    from services.categorization_service import determine_category
except ImportError:
    determine_category = None
    logger.warning("categorization service not found")


try:
    from services.metadata_service import extract_metadata
except ImportError:
    extract_metadata = None
    logger.warning("metadata service not found")



try:
    from services.storage_service import (
        get_storage_analysis,
        get_largest_files,
        get_storage_by_category
    )
except ImportError:
    get_storage_analysis = None
    get_largest_files = None
    get_storage_by_category = None
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


try:
    from ai.gemini import get_embedding
except ImportError:
    get_embedding = None
    logger.warning("get_embedding function not found in gemini.py")

try:
    from services.semantic_service import get_file_text_representation
except ImportError:
    get_file_text_representation = None
    logger.warning("semantic service not found")



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
            
            # Categorize the file (potentially runs I/O signature check; run in thread pool)
            if determine_category:
                file_cat = await asyncio.to_thread(determine_category, file["path"], file["extension"])
                file["category"] = file_cat
            else:
                file["category"] = "Other"
            
            # Extract metadata (potentially runs I/O; run in thread pool)
            if extract_metadata:
                file_meta = await asyncio.to_thread(extract_metadata, file["path"], file["category"], file["extension"])
                import json
                file["meta_data"] = json.dumps(file_meta) if file_meta else None
            else:
                file["meta_data"] = None

            # Generate embedding (potentially runs I/O/network; run in thread pool)
            if get_file_text_representation and get_embedding:
                text_repr = get_file_text_representation(file)
                embedding = await asyncio.to_thread(get_embedding, text_repr)
                file["vector_embedding"] = json.dumps(embedding) if embedding else None
            else:
                file["vector_embedding"] = None


            
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


@app.get("/storage-by-category")
def storage_by_category():

    if not get_storage_by_category:
        return {
            "error": "Storage service not loaded"
        }

    return get_storage_by_category()


@app.get("/file-metadata/{file_id}")
def file_metadata(file_id: int):
    if not SessionLocal or not FileRecord:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database models are not loaded"
        )
    
    db = SessionLocal()
    try:
        record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File record with ID {file_id} not found"
            )
        
        import json
        metadata = {}
        if record.meta_data:
            try:
                metadata = json.loads(record.meta_data)
            except Exception:
                logger.warning("Failed to parse metadata JSON for file ID %d", file_id)
        return metadata
    finally:
        db.close()


@app.get("/security-report")
def security_report():
    if not SessionLocal or not FileRecord:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database models are not loaded"
        )
        
    db = SessionLocal()
    try:
        records = db.query(FileRecord).filter(FileRecord.meta_data.isnot(None)).all()
        
        import json
        grouped_alerts = {
            "unverified_executable": [],
            "contains_api_key": [],
            "contains_password": [],
            "contains_pii_ssn": [],
            "contains_pii_credit_card": []
        }
        
        for record in records:
            try:
                meta = json.loads(record.meta_data)
                alerts = meta.get("security_alerts", [])
                for alert in alerts:
                    if alert in grouped_alerts:
                        grouped_alerts[alert].append({
                            "id": record.id,
                            "name": record.name,
                            "path": record.path,
                            "category": record.category
                        })
            except Exception:
                continue
                
        return grouped_alerts
    finally:
        db.close()


@app.post("/delete-duplicate")
def delete_duplicate(path: str, duplicate_hash: str, confirm: bool = False):
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mandatory confirmation parameter 'confirm=True' is missing or False"
        )
        
    if not SessionLocal or not FileRecord:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database models are not loaded"
        )
        
    db = SessionLocal()
    try:
        record = (
            db.query(FileRecord)
            .filter(FileRecord.path == path, FileRecord.hash == duplicate_hash)
            .first()
        )
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No duplicate file found at path '{path}' with hash '{duplicate_hash}'"
            )
            
        dup_count = db.query(FileRecord).filter(FileRecord.hash == duplicate_hash).count()
        if dup_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Safety violation: Cannot delete the last remaining copy of a duplicate file group."
            )
            
        import os
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete file from disk: {str(e)}"
                )
        else:
            logger.warning("File %s not found on disk, proceeding with database record deletion only", path)
            
        size_bytes = record.size
        db.delete(record)
        db.commit()
        
        return {
            "message": "Duplicate file deleted successfully",
            "path": path,
            "recovered_bytes": size_bytes
        }
    finally:
        db.close()


@app.post("/cleanup-temp")
def cleanup_temp(confirm: bool = False):
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mandatory confirmation parameter 'confirm=True' is missing or False"
        )
        
    if not SessionLocal or not FileRecord:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database models are not loaded"
        )
        
    db = SessionLocal()
    try:
        records = db.query(FileRecord).filter(FileRecord.category == "Temp").all()
        if not records:
            return {
                "message": "No temporary files found to delete",
                "deleted_count": 0,
                "recovered_bytes": 0
            }
            
        import os
        deleted_count = 0
        recovered_bytes = 0
        
        for record in records:
            path = record.path
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logger.warning("Failed to delete temp file %s from disk: %s", path, str(e))
                    continue
            
            recovered_bytes += record.size
            db.delete(record)
            deleted_count += 1
            
        db.commit()
        return {
            "message": "Temporary files cleanup completed",
            "deleted_count": deleted_count,
            "recovered_bytes": recovered_bytes
        }
    finally:
        db.close()


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


@app.get("/semantic-search")
def semantic_search(q: str, limit: int = 10):
    if not SessionLocal or not FileRecord:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database models are not loaded"
        )
    if not q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'q' is required"
        )
    
    if not get_embedding:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI embedding generator is not loaded"
        )
        
    query_emb = get_embedding(q, is_query=True)
    if not query_emb:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate embedding for query"
        )
        
    db = SessionLocal()
    try:
        from services.semantic_service import cosine_similarity
        import json
        
        records = db.query(FileRecord).filter(FileRecord.vector_embedding.isnot(None)).all()
        results = []
        for r in records:
            try:
                emb = json.loads(r.vector_embedding)
                if not emb:
                    continue
                score = cosine_similarity(query_emb, emb)
                results.append({
                    "id": r.id,
                    "name": r.name,
                    "path": r.path,
                    "size": r.size,
                    "extension": r.extension,
                    "category": r.category,
                    "similarity": score
                })
            except Exception:
                continue
                
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]
    finally:
        db.close()


@app.get("/folder-summary")
def folder_summary(folder_path: str):
    if not SessionLocal or not FileRecord:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database models are not loaded"
        )
    if not folder_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'folder_path' is required"
        )
        
    import os
    norm_folder_path = os.path.abspath(folder_path)
    
    db = SessionLocal()
    try:
        # Standardize separator for Windows prefix matching
        prefix = norm_folder_path
        if not prefix.endswith(os.sep):
            prefix += os.sep
            
        # Fetch files matching/under folder_path
        records = db.query(FileRecord).filter(
            (FileRecord.path == norm_folder_path) |
            (FileRecord.path.like(prefix + "%"))
        ).all()
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No indexed files found in folder path '{folder_path}'"
            )
            
        # Compile stats
        total_count = len(records)
        total_size = sum(r.size for r in records)
        
        # Categories breakdown
        categories = {}
        for r in records:
            cat = r.category or "Other"
            categories[cat] = categories.get(cat, 0) + 1
            
        # Compile files list details for prompt context (limit to 50 files)
        import json
        files_details = []
        alerts_count = 0
        for r in records[:50]:
            meta = {}
            if r.meta_data:
                try:
                    meta = json.loads(r.meta_data)
                except Exception:
                    pass
            alerts = meta.get("security_alerts", [])
            alerts_count += len(alerts)
            
            detail = f"- {r.name} ({r.category}, {r.size} bytes)"
            if alerts:
                detail += f" [ALERTS: {', '.join(alerts)}]"
            files_details.append(detail)
            
        if len(records) > 50:
            files_details.append(f"... and {len(records) - 50} more files.")
            
        files_list_text = "\n".join(files_details)
        
        from ai.gemini import ask_ai
        
        prompt = f"""
You are AegisAI, an intelligent Digital Intelligence Assistant for Windows.
Summarize the contents of the directory: '{norm_folder_path}'.
Here is the context of the files located in this directory:
- Total file count: {total_count}
- Total size: {total_size} bytes
- Category counts: {json.dumps(categories)}
- Total security alerts: {alerts_count}
- Files list:
{files_list_text}

Provide a short, professional, and friendly summary of this folder. Describe what kind of folder this is (e.g. Code workspace, Pictures, Documents) based on the categories, list key documents/media files, point out any security warnings (like plain-text passwords or scripts), and suggest any cleanup optimization tips (like duplicates).
"""
        summary_text = ask_ai(prompt)
        
        return {
            "folder_path": norm_folder_path,
            "total_files": total_count,
            "total_size_bytes": total_size,
            "category_distribution": categories,
            "summary": summary_text
        }
    finally:
        db.close()
