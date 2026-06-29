import unittest
import tempfile
import os
import shutil
from fastapi import HTTPException

from database.db import SessionLocal
from database.models import FileRecord
from database.init_db import create_tables
from services.file_service import save_files
from main import delete_duplicate, cleanup_temp


class TestCleanupEngine(unittest.TestCase):

    def setUp(self):
        create_tables()
        self.db = SessionLocal()
        self.db.query(FileRecord).delete()
        self.db.commit()
        
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.temp_dir)

    def test_delete_duplicate_without_confirm_fails(self):
        with self.assertRaises(HTTPException) as ctx:
            delete_duplicate(path="C:\\dummy.txt", duplicate_hash="h1", confirm=False)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("confirm=True", ctx.exception.detail)

    def test_delete_duplicate_last_copy_fails(self):
        # Insert exactly 1 record with hash "h1" (last copy)
        test_files = [
            {
                "name": "file1.txt",
                "path": "C:\\file1.txt",
                "size": 100,
                "extension": ".txt",
                "category": "Documents",
                "hash": "h1"
            }
        ]
        save_files(test_files)
        
        # Try to delete it (should fail because dup_count == 1)
        with self.assertRaises(HTTPException) as ctx:
            delete_duplicate(path="C:\\file1.txt", duplicate_hash="h1", confirm=True)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("last remaining copy", ctx.exception.detail)

    def test_delete_duplicate_succeeds(self):
        # Create temp files on disk
        f1_path = os.path.join(self.temp_dir, "dup1.txt")
        f2_path = os.path.join(self.temp_dir, "dup2.txt")
        
        with open(f1_path, "w") as f:
            f.write("hello")
        with open(f2_path, "w") as f:
            f.write("hello")
            
        test_files = [
            {
                "name": "dup1.txt",
                "path": f1_path,
                "size": 5,
                "extension": ".txt",
                "category": "Documents",
                "hash": "hash_val"
            },
            {
                "name": "dup2.txt",
                "path": f2_path,
                "size": 5,
                "extension": ".txt",
                "category": "Documents",
                "hash": "hash_val"
            }
        ]
        save_files(test_files)
        
        # Delete dup1 (should succeed as dup2 exists)
        response = delete_duplicate(path=f1_path, duplicate_hash="hash_val", confirm=True)
        self.assertEqual(response["message"], "Duplicate file deleted successfully")
        self.assertEqual(response["recovered_bytes"], 5)
        
        # Verify file is deleted from disk
        self.assertFalse(os.path.exists(f1_path))
        self.assertTrue(os.path.exists(f2_path))
        
        # Verify record is deleted from database
        record1 = self.db.query(FileRecord).filter(FileRecord.path == f1_path).first()
        self.assertIsNone(record1)
        record2 = self.db.query(FileRecord).filter(FileRecord.path == f2_path).first()
        self.assertIsNotNone(record2)

    def test_cleanup_temp_without_confirm_fails(self):
        with self.assertRaises(HTTPException) as ctx:
            cleanup_temp(confirm=False)
        self.assertEqual(ctx.exception.status_code, 400)

    def test_cleanup_temp_succeeds(self):
        # Create temp files on disk
        temp_path1 = os.path.join(self.temp_dir, "temp1.tmp")
        temp_path2 = os.path.join(self.temp_dir, "temp2.log")
        doc_path = os.path.join(self.temp_dir, "doc.pdf")
        
        for path in [temp_path1, temp_path2, doc_path]:
            with open(path, "w") as f:
                f.write("abc")
                
        test_files = [
            {"name": "temp1.tmp", "path": temp_path1, "size": 3, "extension": ".tmp", "category": "Temp", "hash": "h1"},
            {"name": "temp2.log", "path": temp_path2, "size": 3, "extension": ".log", "category": "Temp", "hash": "h2"},
            {"name": "doc.pdf", "path": doc_path, "size": 3, "extension": ".pdf", "category": "Documents", "hash": "h3"}
        ]
        save_files(test_files)
        
        # Run cleanup
        response = cleanup_temp(confirm=True)
        self.assertEqual(response["deleted_count"], 2)
        self.assertEqual(response["recovered_bytes"], 6)
        
        # Verify files deleted from disk
        self.assertFalse(os.path.exists(temp_path1))
        self.assertFalse(os.path.exists(temp_path2))
        self.assertTrue(os.path.exists(doc_path))
        
        # Verify DB records
        temp1_record = self.db.query(FileRecord).filter(FileRecord.path == temp_path1).first()
        self.assertIsNone(temp1_record)
        doc_record = self.db.query(FileRecord).filter(FileRecord.path == doc_path).first()
        self.assertIsNotNone(doc_record)


if __name__ == "__main__":
    unittest.main()
