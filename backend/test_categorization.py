import unittest
import tempfile
import os
import shutil
from services.categorization_service import determine_category
from database.db import SessionLocal, engine
from database.models import FileRecord, Base
from database.init_db import create_tables
from services.storage_service import get_storage_by_category
from services.file_service import save_files

class TestCategorizationService(unittest.TestCase):
    
    def test_suffix_mappings(self):
        # Media
        self.assertEqual(determine_category("dummy.png", ".png"), "Media")
        self.assertEqual(determine_category("dummy.jpg", ".jpg"), "Media")
        self.assertEqual(determine_category("dummy.mp3", ".mp3"), "Media")
        
        # Documents
        self.assertEqual(determine_category("dummy.txt", ".txt"), "Documents")
        self.assertEqual(determine_category("dummy.pdf", ".pdf"), "Documents")
        
        # Code
        self.assertEqual(determine_category("dummy.py", ".py"), "Code")
        self.assertEqual(determine_category("dummy.js", ".js"), "Code")
        
        # Archives
        self.assertEqual(determine_category("dummy.zip", ".zip"), "Archives")
        self.assertEqual(determine_category("dummy.tar.gz", ".gz"), "Archives")
        
        # Temp
        self.assertEqual(determine_category("dummy.tmp", ".tmp"), "Temp")
        self.assertEqual(determine_category("dummy.log", ".log"), "Temp")
        
        # Other
        self.assertEqual(determine_category("dummy.xyz", ".xyz"), "Other")
        
    def test_magic_bytes_fallback(self):
        # Create temp files to test header parsing
        temp_dir = tempfile.mkdtemp()
        try:
            # 1. PNG Image header (Media)
            png_path = os.path.join(temp_dir, "test_png")
            with open(png_path, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\nSome extra image bytes")
            self.assertEqual(determine_category(png_path, ""), "Media")
            
            # 2. PDF Document header (Documents)
            pdf_path = os.path.join(temp_dir, "test_pdf")
            with open(pdf_path, "wb") as f:
                f.write(b"%PDF-1.5\n%EOF")
            self.assertEqual(determine_category(pdf_path, ""), "Documents")
            
            # 3. ZIP Archive container (Archives)
            zip_path = os.path.join(temp_dir, "test_zip")
            with open(zip_path, "wb") as f:
                f.write(b"PK\x03\x04\nRandom zip data")
            self.assertEqual(determine_category(zip_path, ""), "Archives")
            
            # 4. ZIP Archive container with .docx extension (Documents)
            docx_path = os.path.join(temp_dir, "test_docx.docx")
            with open(docx_path, "wb") as f:
                f.write(b"PK\x03\x04\nDocx xml structure")
            self.assertEqual(determine_category(docx_path, ".docx"), "Documents")
            
            # 5. Invalid/Unknown file
            unknown_path = os.path.join(temp_dir, "test_unknown")
            with open(unknown_path, "wb") as f:
                f.write(b"Hello world plain text")
            self.assertEqual(determine_category(unknown_path, ""), "Other")
            
        finally:
            shutil.rmtree(temp_dir)

class TestDatabaseAggregation(unittest.TestCase):
    
    def setUp(self):
        # Recreate tables in SQLite and clean database
        create_tables()
        db = SessionLocal()
        try:
            db.query(FileRecord).delete()
            db.commit()
        finally:
            db.close()
            
    def test_storage_by_category(self):
        # 1. Insert dummy files
        test_files = [
            {"name": "a.py", "path": "C:\\a.py", "size": 100, "extension": ".py", "category": "Code", "hash": "h1"},
            {"name": "b.py", "path": "C:\\b.py", "size": 150, "extension": ".py", "category": "Code", "hash": "h2"},
            {"name": "c.png", "path": "C:\\c.png", "size": 500, "extension": ".png", "category": "Media", "hash": "h3"},
            {"name": "d.zip", "path": "C:\\d.zip", "size": 1000, "extension": ".zip", "category": "Archives", "hash": "h4"},
            {"name": "e.txt", "path": "C:\\e.txt", "size": 250, "extension": ".txt", "category": "Documents", "hash": "h5"}
        ]
        
        # Save files
        save_files(test_files)
        
        # 2. Query statistics by category
        stats = get_storage_by_category()
        
        # 3. Assert counts and sizes
        self.assertIn("Code", stats)
        self.assertEqual(stats["Code"]["count"], 2)
        self.assertEqual(stats["Code"]["total_size_bytes"], 250)
        
        self.assertIn("Media", stats)
        self.assertEqual(stats["Media"]["count"], 1)
        self.assertEqual(stats["Media"]["total_size_bytes"], 500)
        
        self.assertIn("Archives", stats)
        self.assertEqual(stats["Archives"]["count"], 1)
        self.assertEqual(stats["Archives"]["total_size_bytes"], 1000)
        
        self.assertIn("Documents", stats)
        self.assertEqual(stats["Documents"]["count"], 1)
        self.assertEqual(stats["Documents"]["total_size_bytes"], 250)

if __name__ == "__main__":
    unittest.main()
