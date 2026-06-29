from sqlalchemy import func
from database.db import SessionLocal
from database.models import FileRecord


def get_storage_analysis():

    db = SessionLocal()

    try:

        files = db.query(FileRecord).all()

        total_files = len(files)

        total_size = sum(file.size for file in files)

        average_size = (
            total_size / total_files
            if total_files > 0
            else 0
        )

        return {
            "total_files": total_files,
            "total_storage_bytes": total_size,
            "average_file_size_bytes": average_size
        }

    finally:
        db.close()


def get_largest_files(limit=20):

    db = SessionLocal()

    try:

        files = (
            db.query(FileRecord)
            .order_by(FileRecord.size.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "name": file.name,
                "path": file.path,
                "size_bytes": file.size
            }
            for file in files
        ]

    finally:
        db.close()


def get_storage_by_category():
    db = SessionLocal()
    try:
        results = (
            db.query(
                FileRecord.category,
                func.count(FileRecord.id).label("count"),
                func.sum(FileRecord.size).label("total_size")
            )
            .group_by(FileRecord.category)
            .all()
        )
        return {
            row.category or "Other": {
                "count": row.count,
                "total_size_bytes": row.total_size or 0
            }
            for row in results
        }
    finally:
        db.close()