import unittest
import tempfile
import os
import shutil
import json
import zipfile
from unittest.mock import patch, MagicMock

# Database / FastAPI test imports
from database.db import SessionLocal
from database.models import FileRecord
from database.init_db import create_tables
from services.file_service import save_files

# Services to test
from services.metadata_service import (
    extract_image_dimensions,
    extract_image_metadata,
    extract_office_metadata,
    extract_pdf_metadata,
    extract_audio_metadata,
    extract_metadata
)


class TestMetadataService(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_png_dimensions(self):
        # Create a valid PNG-like byte array header
        # Header + IHDR chunk type + 4 bytes width + 4 bytes height
        png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x03\x20\x00\x00\x02\x58\x08\x06\x00\x00\x00"
        png_path = os.path.join(self.temp_dir, "test.png")
        with open(png_path, "wb") as f:
            f.write(png_data)
            
        w, h = extract_image_dimensions(png_path)
        self.assertEqual(w, 800)  # 0x00000320 = 800
        self.assertEqual(h, 600)  # 0x00000258 = 600

    def test_gif_dimensions(self):
        # Header GIF89a + 2 bytes width (little-endian) + 2 bytes height
        gif_data = b"GIF89a\x20\x03\x58\x02\x00\x00\x00"
        gif_path = os.path.join(self.temp_dir, "test.gif")
        with open(gif_path, "wb") as f:
            f.write(gif_data)
            
        w, h = extract_image_dimensions(gif_path)
        self.assertEqual(w, 800)  # 0x0320 = 800
        self.assertEqual(h, 600)  # 0x0258 = 600

    def test_jpeg_dimensions(self):
        # SOI marker (\xff\xd8) + SOF0 marker (\xff\xc0) + length + precision + height + width
        jpeg_data = b"\xff\xd8\xff\xc0\x00\x11\x08\x02\x58\x03\x20\x03\x01\x22\x00\x02\x11\x01"
        jpeg_path = os.path.join(self.temp_dir, "test.jpg")
        with open(jpeg_path, "wb") as f:
            f.write(jpeg_data)
            
        w, h = extract_image_dimensions(jpeg_path)
        self.assertEqual(w, 800)  # 0x0320 = 800
        self.assertEqual(h, 600)  # 0x0258 = 600

    def test_office_metadata_extraction(self):
        # Create a mock docx ZIP archive
        docx_path = os.path.join(self.temp_dir, "test.docx")
        
        core_xml = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                           xmlns:dc="http://purl.org/dc/elements/1.1/">
            <dc:creator>John Doe</dc:creator>
        </cp:coreProperties>
        """
        
        app_xml = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
                    xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
            <Pages>12</Pages>
        </Properties>
        """
        
        with zipfile.ZipFile(docx_path, "w") as z:
            z.writestr("docProps/core.xml", core_xml)
            z.writestr("docProps/app.xml", app_xml)
            
        meta = extract_office_metadata(docx_path)
        self.assertEqual(meta.get("author"), "John Doe")
        self.assertEqual(meta.get("pages"), 12)

    def test_pdf_metadata_extraction(self):
        # Minimal valid-ish PDF with author and count
        # (Using a mock for PdfReader to make it decoupled from pypdf library variations)
        pdf_path = os.path.join(self.temp_dir, "test.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4...")
            
        mock_meta = MagicMock()
        mock_meta.author = "PDF Author"
        
        mock_reader = MagicMock()
        mock_reader.metadata = mock_meta
        mock_reader.pages = [1, 2, 3, 4, 5]
        
        with patch("services.metadata_service.PdfReader", return_value=mock_reader):
            meta = extract_pdf_metadata(pdf_path)
            self.assertEqual(meta.get("author"), "PDF Author")
            self.assertEqual(meta.get("pages"), 5)

    def test_audio_metadata_extraction(self):
        mp3_path = os.path.join(self.temp_dir, "test.mp3")
        with open(mp3_path, "wb") as f:
            f.write(b"ID3...")
            
        mock_tag = MagicMock()
        mock_tag.artist = "Audio Artist"
        mock_tag.duration = 180.5
        
        with patch("services.metadata_service.TinyTag.get", return_value=mock_tag):
            meta = extract_audio_metadata(mp3_path)
            self.assertEqual(meta.get("artist"), "Audio Artist")
            self.assertEqual(meta.get("duration"), 180)

    def test_dispatcher(self):
        # Test default/fallback cases of the dispatcher
        # If file does not exist, should return {}
        self.assertEqual(extract_metadata("nonexistent.xyz", "Code", ".py"), {})


class TestDatabaseMetadataIntegration(unittest.TestCase):

    def setUp(self):
        create_tables()
        self.db = SessionLocal()
        # Clean any preexisting records
        self.db.query(FileRecord).delete()
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_saving_and_querying_metadata(self):
        # 1. Save record with JSON-serialized metadata
        metadata_dict = {"width": 1920, "height": 1080, "creation_date": "2026-06-26T12:00:00Z"}
        serialized = json.dumps(metadata_dict)
        
        test_files = [
            {
                "name": "pic.png",
                "path": "C:\\pic.png",
                "size": 50000,
                "extension": ".png",
                "category": "Media",
                "hash": "h123",
                "meta_data": serialized
            }
        ]
        
        save_files(test_files)
        
        # 2. Retrieve record and verify the meta_data is correctly saved
        record = self.db.query(FileRecord).filter(FileRecord.path == "C:\\pic.png").first()
        self.assertIsNotNone(record)
        self.assertEqual(record.meta_data, serialized)
        
        # Parse it back
        parsed = json.loads(record.meta_data)
        self.assertEqual(parsed["width"], 1920)
        self.assertEqual(parsed["creation_date"], "2026-06-26T12:00:00Z")

    def test_file_metadata_api_endpoint(self):
        # 1. Insert a dummy record
        test_files = [
            {
                "name": "doc.pdf",
                "path": "C:\\doc.pdf",
                "size": 12345,
                "extension": ".pdf",
                "category": "Documents",
                "hash": "h999",
                "meta_data": json.dumps({"author": "Alice", "pages": 42})
            }
        ]
        save_files(test_files)
        
        # 2. Retrieve the generated ID
        record = self.db.query(FileRecord).filter(FileRecord.path == "C:\\doc.pdf").first()
        self.assertIsNotNone(record)
        
        # 3. Call the API endpoint function directly
        from main import file_metadata
        result = file_metadata(record.id)
        
        # 4. Verify output
        self.assertEqual(result.get("author"), "Alice")
        self.assertEqual(result.get("pages"), 42)



if __name__ == "__main__":
    unittest.main()
