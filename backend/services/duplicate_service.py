try:
    from ..database.db import SessionLocal
    from ..database.models import FileRecord
except Exception:
    from database.db import SessionLocal
    from database.models import FileRecord

def find_duplicates():

    db = SessionLocal()

    try:

        files = db.query(FileRecord).all()

        hashes = {}

        duplicates = []

        for file in files:

            if not file.hash:
                continue

            if file.hash not in hashes:
                hashes[file.hash] = []

            hashes[file.hash].append(file)

        for hash_value, group in hashes.items():

            if len(group) > 1:

                duplicates.append({
                    "hash": hash_value,
                    "count": len(group),
                    "files": [
                        {
                            "name": f.name,
                            "path": f.path,
                            "size": f.size
                        }
                        for f in group
                    ]
                })

        return duplicates

    finally:
        db.close()