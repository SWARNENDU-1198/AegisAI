import unittest
import tempfile
import os
import shutil
import json

from database.db import SessionLocal
from database.models import FileRecord
from database.init_db import create_tables
from services.file_service import save_files
from services.security_service import analyze_file_security
from services.metadata_service import extract_metadata
from main import security_report


class TestSecurityScanner(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_secrets_detection(self):
        # 1. Test API Key
        path_api = os.path.join(self.temp_dir, "keys.txt")
        with open(path_api, "w", encoding="utf-8") as f:
            f.write("my_secret_key = 'abc123xyz789ABCDEF0'\n")
        alerts = analyze_file_security(path_api, ".txt")
        self.assertIn("contains_api_key", alerts)

        # 2. Test Password
        path_pwd = os.path.join(self.temp_dir, "config.json")
        with open(path_pwd, "w", encoding="utf-8") as f:
            f.write('{"db_password": "supersecretpassword123"}')
        alerts = analyze_file_security(path_pwd, ".json")
        self.assertIn("contains_password", alerts)

        # 3. Test SSN
        path_ssn = os.path.join(self.temp_dir, "pii.txt")
        with open(path_ssn, "w", encoding="utf-8") as f:
            f.write("User SSN is 000-12-3456 in document.")
        alerts = analyze_file_security(path_ssn, ".txt")
        self.assertIn("contains_pii_ssn", alerts)

        # 4. Test Credit Card
        path_cc = os.path.join(self.temp_dir, "billing.csv")
        with open(path_cc, "w", encoding="utf-8") as f:
            f.write("Name,CardNumber\nJohn,1234-5678-9012-3456\n")
        alerts = analyze_file_security(path_cc, ".csv")
        self.assertIn("contains_pii_credit_card", alerts)

    def test_dangerous_executables(self):
        # Unverified executables should be flagged purely by extension
        alerts = analyze_file_security("C:\\dangerous_script.ps1", ".ps1")
        self.assertIn("unverified_executable", alerts)

        alerts = analyze_file_security("C:\\installer.msi", ".msi")
        self.assertIn("unverified_executable", alerts)

        # Normal file should not be flagged
        alerts = analyze_file_security("C:\\safe_doc.pdf", ".pdf")
        self.assertEqual(len(alerts), 0)

    def test_integration_with_metadata(self):
        # Create a file with a secret
        path = os.path.join(self.temp_dir, "key.env")
        with open(path, "w", encoding="utf-8") as f:
            f.write("API_KEY = \"1234567890abcdef123\"")
            
        meta = extract_metadata(path, "Code", ".env")
        self.assertIn("security_alerts", meta)
        self.assertIn("contains_api_key", meta["security_alerts"])


class TestSecurityReportAPI(unittest.TestCase):

    def setUp(self):
        create_tables()
        self.db = SessionLocal()
        self.db.query(FileRecord).delete()
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_security_report_endpoint(self):
        # Save a file with a security alert in meta_data
        test_files = [
            {
                "name": "hacker.bat",
                "path": "C:\\hacker.bat",
                "size": 100,
                "extension": ".bat",
                "category": "Code",
                "hash": "hbat",
                "meta_data": json.dumps({"security_alerts": ["unverified_executable"]})
            },
            {
                "name": "password.txt",
                "path": "C:\\password.txt",
                "size": 200,
                "extension": ".txt",
                "category": "Documents",
                "hash": "hpwd",
                "meta_data": json.dumps({"security_alerts": ["contains_password"]})
            }
        ]
        save_files(test_files)

        # Call endpoint directly
        report = security_report()
        
        self.assertIn("unverified_executable", report)
        self.assertEqual(len(report["unverified_executable"]), 1)
        self.assertEqual(report["unverified_executable"][0]["name"], "hacker.bat")
        
        self.assertIn("contains_password", report)
        self.assertEqual(len(report["contains_password"]), 1)
        self.assertEqual(report["contains_password"][0]["name"], "password.txt")


if __name__ == "__main__":
    unittest.main()
