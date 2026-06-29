import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import json

from services.semantic_service import cosine_similarity, get_file_text_representation
from database.db import SessionLocal
from database.models import FileRecord, Base
from database.init_db import create_tables
from main import semantic_search, folder_summary

class TestSemanticService(unittest.TestCase):
    
    def test_cosine_similarity(self):
        # Identical vectors
        v1 = [1.0, 2.0, 3.0]
        v2 = [1.0, 2.0, 3.0]
        self.assertAlmostEqual(cosine_similarity(v1, v2), 1.0)
        
        # Orthogonal vectors
        v1 = [1.0, 0.0]
        v2 = [0.0, 1.0]
        self.assertAlmostEqual(cosine_similarity(v1, v2), 0.0)
        
        # Opposing vectors
        v1 = [1.0, -1.0]
        v2 = [-1.0, 1.0]
        self.assertAlmostEqual(cosine_similarity(v1, v2), -1.0)
        
        # Edge cases: empty or different dimensions
        self.assertEqual(cosine_similarity([], [1.0]), 0.0)
        self.assertEqual(cosine_similarity([1.0, 2.0], [1.0]), 0.0)
        self.assertEqual(cosine_similarity([0.0, 0.0], [1.0, 2.0]), 0.0)

    def test_get_file_text_representation(self):
        file = {
            "name": "report.pdf",
            "category": "Documents",
            "extension": ".pdf",
            "meta_data": json.dumps({"author": "Alice", "pages": 10})
        }
        repr_str = get_file_text_representation(file)
        self.assertIn("Name: report.pdf", repr_str)
        self.assertIn("Category: Documents", repr_str)
        self.assertIn("Extension: .pdf", repr_str)
        self.assertIn("Metadata: " + json.dumps({"author": "Alice", "pages": 10}), repr_str)
        
        # Test dict format
        file_dict = {
            "name": "report.pdf",
            "category": "Documents",
            "extension": ".pdf",
            "meta_data": {"author": "Alice", "pages": 10}
        }
        repr_str_dict = get_file_text_representation(file_dict)
        self.assertEqual(repr_str, repr_str_dict)
        
        # Test None format
        file_none = {
            "name": "report.pdf",
            "category": "Documents",
            "extension": ".pdf",
            "meta_data": None
        }
        repr_str_none = get_file_text_representation(file_none)
        self.assertIn("Metadata: ", repr_str_none)


class TestSemanticSearchEndpoints(unittest.TestCase):
    
    def setUp(self):
        # Ensure database tables exist and are clean
        create_tables()
        db = SessionLocal()
        try:
            db.query(FileRecord).delete()
            db.commit()
        finally:
            db.close()

    @patch("main.get_embedding")
    def test_semantic_search_endpoint(self, mock_get_embedding):
        # Setup mock embeddings
        # Query: "reports" -> [1.0, 0.0]
        # File 1: "financial_report.pdf" -> [1.0, 0.0] (Similarity = 1.0)
        # File 2: "vacation_photo.png" -> [0.0, 1.0] (Similarity = 0.0)
        mock_get_embedding.side_effect = lambda text, is_query=False: [1.0, 0.0] if "reports" in text else [0.0, 1.0]
        
        # Save mock files into database
        db = SessionLocal()
        try:
            f1 = FileRecord(
                name="financial_report.pdf",
                path="C:\\financial_report.pdf",
                size=1024,
                extension=".pdf",
                category="Documents",
                hash="h1",
                vector_embedding=json.dumps([1.0, 0.0])
            )
            f2 = FileRecord(
                name="vacation_photo.png",
                path="C:\\vacation_photo.png",
                size=2048,
                extension=".png",
                category="Media",
                hash="h2",
                vector_embedding=json.dumps([0.0, 1.0])
            )
            db.add(f1)
            db.add(f2)
            db.commit()
        finally:
            db.close()
            
        # Perform query directly by calling endpoint function
        data = semantic_search(q="reports")
        
        self.assertEqual(len(data), 2)
        
        # Check sort order and details
        self.assertEqual(data[0]["name"], "financial_report.pdf")
        self.assertAlmostEqual(data[0]["similarity"], 1.0)
        
        self.assertEqual(data[1]["name"], "vacation_photo.png")
        self.assertAlmostEqual(data[1]["similarity"], 0.0)

    @patch("ai.gemini.ask_ai")
    def test_folder_summary_endpoint(self, mock_ask_ai):
        mock_ask_ai.return_value = "Mocked AI Folder Summary"
        
        # Save files under a specific directory prefix
        db = SessionLocal()
        try:
            f1 = FileRecord(
                name="main.py",
                path="C:\\project\\backend\\main.py",
                size=150,
                extension=".py",
                category="Code",
                hash="h1",
                meta_data=json.dumps({"security_alerts": ["unverified_executable"]})
            )
            f2 = FileRecord(
                name="readme.md",
                path="C:\\project\\readme.md",
                size=300,
                extension=".md",
                category="Documents",
                hash="h2"
            )
            f3 = FileRecord(
                name="other.txt",
                path="C:\\other\\other.txt",
                size=500,
                extension=".txt",
                category="Documents",
                hash="h3"
            )
            db.add(f1)
            db.add(f2)
            db.add(f3)
            db.commit()
        finally:
            db.close()
            
        # Get folder summary of project directory
        # The endpoint resolves absolute paths, let's query with "C:\\project"
        data = folder_summary(folder_path="C:\\project")
        
        self.assertIn("folder_path", data)
        self.assertEqual(data["total_files"], 2)
        self.assertEqual(data["total_size_bytes"], 450)
        self.assertEqual(data["category_distribution"]["Code"], 1)
        self.assertEqual(data["category_distribution"]["Documents"], 1)
        self.assertEqual(data["summary"], "Mocked AI Folder Summary")

    @patch("services.chat_service.get_embedding")
    @patch("services.chat_service.ask_ai")
    def test_chat_with_semantic_search(self, mock_ask_ai, mock_get_embedding):
        from services.chat_service import answer_question
        
        mock_get_embedding.return_value = [1.0, 0.0]
        
        captured_prompt = None
        def mock_ask_ai_fn(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            return "Mocked Chat Response"
        mock_ask_ai.side_effect = mock_ask_ai_fn
        
        db = SessionLocal()
        try:
            f = FileRecord(
                name="secret_passwords.txt",
                path="C:\\secret_passwords.txt",
                size=123,
                extension=".txt",
                category="Documents",
                hash="h123",
                vector_embedding=json.dumps([1.0, 0.0])
            )
            db.add(f)
            db.commit()
        finally:
            db.close()
            
        res = answer_question("where are my passwords?")
        
        self.assertEqual(res, "Mocked Chat Response")
        self.assertIsNotNone(captured_prompt)
        self.assertIn("secret_passwords.txt", captured_prompt)
        self.assertIn("Similarity: 1.000", captured_prompt)


if __name__ == "__main__":
    unittest.main()
