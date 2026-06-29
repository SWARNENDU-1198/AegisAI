# Phase 2: File Categorization Engine - Research

This document outlines the technical research and architecture decisions for implementing the file categorization engine.

## 1. File Signatures (Magic Bytes)

Reading file suffixes is extremely fast, but suffixes can be missing or modified. Fulfilling the requirement to map files based on "suffixes and file structures" involves reading the first few bytes (the magic bytes) of files when suffixes are ambiguous.

### Common File Signatures
We research the standard signatures for our logical categories:
- **JPEG Images:** Start with `FF D8 FF`
- **PNG Images:** Start with `89 50 4E 47 0D 0A 1A 0A` (UTF-8: `\x89PNG\r\n\x1a\n`)
- **GIF Images:** Start with `47 49 46 38 37 61` or `47 49 46 38 39 61` (ASCII: `GIF87a`, `GIF89a`)
- **PDF Documents:** Start with `25 50 44 46` (ASCII: `%PDF`)
- **ZIP Archives / Office Documents:** Start with `50 4B 03 04` (ASCII: `PK\x03\x04`). This is a generic zip container signature. Suffix check can distinguish regular ZIPs from office documents (DOCX, XLSX, PPTX).
- **Executables (System):** Start with `4D 5A` (ASCII: `MZ` header)

### Performance Mitigation
Reading files from disk adds I/O overhead. To prevent performance degradation during large directory scans (e.g. 100,000+ files):
1. Categorization will check the file suffix (extension) first. Suffix lookup is in-memory and O(1).
2. If the suffix matches our mapping dictionary, we immediately assign the category.
3. If the suffix is empty (`""`) or unrecognized, we fall back to opening the file in binary mode (`"rb"`) and reading the first 8 bytes.
4. This ensures that only a tiny fraction of files undergo I/O reads for signature analysis, maintaining indexing speed.

---

## 2. SQLite Schema Migrations in SQLAlchemy

Since AegisAI uses SQLite, the database schema is defined as a local file (`aegisai.db`). When adding the `category` column to the `FileRecord` model, existing databases will throw `OperationalError: no such column: category` on startup.

To resolve this without forcing a destructive drop/recreate, we can run a safe alter table query on database initialization:
```python
from sqlalchemy import text

def run_migrations(engine):
    with engine.connect() as conn:
        try:
            # Get table details using SQLite PRAGMA
            info = conn.execute(text("PRAGMA table_info(files)")).fetchall()
            columns = [col[1] for col in info]
            if "category" not in columns:
                conn.execute(text("ALTER TABLE files ADD COLUMN category VARCHAR"))
                conn.commit()
        except Exception:
            # Fail silently to allow normal startup if table doesn't exist yet
            pass
```

---

## 3. SQLAlchemy Database Aggregation

To fetch categorization statistics (`CAT-02` / `/storage-by-category`), executing `db.query(FileRecord).all()` and calculating sums in Python is inefficient for 100,000+ records.

Instead, we use SQLAlchemy group-by queries which delegate the aggregation to the SQLite engine:
```python
from sqlalchemy import func

def get_storage_by_category(db):
    return (
        db.query(
            FileRecord.category,
            func.count(FileRecord.id).label("count"),
            func.sum(FileRecord.size).label("total_size_bytes")
        )
        .group_by(FileRecord.category)
        .all()
    )
```
This reduces database fetch memory overhead to O(C) where C is the number of categories (max 6 rows).

---

## 4. Validation Architecture

We will verify this implementation using automated tests:
1. **Schema Check:** Confirm the database has the `category` column.
2. **Rule Verification:** Test files with specific extensions are classified correctly (e.g., `.py` -> Code, `.pdf` -> Documents).
3. **Magic Byte Verification:** Test files with unknown extensions containing image or PDF headers are correctly resolved.
4. **Aggregate Verification:** Seed dummy records for multiple categories and confirm `/storage-by-category` returns accurate mathematical sums and counts.
