try:
    from ..database.db import SessionLocal
    from ..database.models import FileRecord
except Exception:
    from database.db import SessionLocal
    from database.models import FileRecord

def save_files(file_list):

    db = SessionLocal()

    try:

        for file in file_list:

            exists = (
                db.query(FileRecord)
                .filter(FileRecord.path == file["path"])
                .first()
            )

            if not exists:

                db.add(
                    FileRecord(
                        name=file["name"],
                        path=file["path"],
                        size=file["size"],
                        extension=file["extension"],
                        hash=file["hash"]
                    )
                )

        db.commit()

    finally:
        db.close()