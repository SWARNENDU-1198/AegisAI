import logging
from typing import List, Dict, Any
from sqlalchemy.exc import SQLAlchemyError

try:
    from ..database.db import SessionLocal
    from ..database.models import FileRecord
except Exception:
    from database.db import SessionLocal
    from database.models import FileRecord

logger = logging.getLogger(__name__)

def save_files(file_list: List[Dict[str, Any]]) -> None:
    """Save scanned files metadata to SQLite database in bulk.
    
    Performs a set-based path existence check to prevent duplicate
    inserts and eliminate N+1 select queries.
    
    Args:
        file_list: A list of dictionaries containing file metadata.
    """
    if not file_list:
        logger.info("No files to save.")
        return

    db = SessionLocal()
    try:
        # Fetch all existing paths in a single query
        existing_paths = {row[0] for row in db.query(FileRecord.path).all()}
        print(f"DEBUG_SAVE: file_list length: {len(file_list)}")
        print(f"DEBUG_SAVE: existing_paths length: {len(existing_paths)}")
        if existing_paths:
            print(f"DEBUG_SAVE: sample existing paths: {list(existing_paths)[:3]}")
        if file_list:
            print(f"DEBUG_SAVE: sample file_list paths: {[f['path'] for f in file_list[:3]]}")
            
        # Filter out already existing files and duplicates within file_list itself
        to_insert = []
        seen_in_batch = set()
        for file in file_list:
            path = file["path"]
            if path not in existing_paths and path not in seen_in_batch:
                seen_in_batch.add(path)
                to_insert.append({
                    "name": file["name"],
                    "path": path,
                    "size": file["size"],
                    "extension": file["extension"],
                    "hash": file.get("hash"),
                    "category": file.get("category", "Other"),
                    "meta_data": file.get("meta_data"),
                    "vector_embedding": file.get("vector_embedding")
                })

        
        if to_insert:
            db.bulk_insert_mappings(FileRecord, to_insert)
            db.commit()
            logger.info("Successfully bulk inserted %d new file records.", len(to_insert))
        else:
            logger.info("All files already exist in the database. No new inserts.")
            
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Failed to bulk save files to database: %s", str(e))
        raise e
    finally:
        db.close()