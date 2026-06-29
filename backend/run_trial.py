import sys
import os
import shutil
import asyncio
import time
import json
from pathlib import Path

# Add backend directory to path
backend_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)

# Import original config and main app components
import config
import main
from database.init_db import create_tables

# Define trial directory
TRIAL_DIR = os.path.join(backend_dir, "trial_scan_folder")

def setup_trial_files():
    print(f"Creating trial directory at: {TRIAL_DIR}")
    if os.path.exists(TRIAL_DIR):
        shutil.rmtree(TRIAL_DIR)
    os.makedirs(TRIAL_DIR, exist_ok=True)
    
    # 1. Media PNG (Width: 800, Height: 600)
    png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x03\x20\x00\x00\x02\x58\x08\x06\x00\x00\x00"
    with open(os.path.join(TRIAL_DIR, "image_test.png"), "wb") as f:
        f.write(png_data)
        
    # 2. Duplicate PNG
    with open(os.path.join(TRIAL_DIR, "image_test_copy.png"), "wb") as f:
        f.write(png_data)
        
    # 3. Document with sensitive details (API Key, Password)
    sensitive_data = """
    # Project Config
    # Do not share this file!
    api_key = "sk-proj-9876543210fedcba9876543210fedcba"
    db_password = "supersecretpassword123"
    """
    with open(os.path.join(TRIAL_DIR, "secrets.txt"), "w") as f:
        f.write(sensitive_data)
        
    # 4. Dangerous script
    with open(os.path.join(TRIAL_DIR, "installer.bat"), "w") as f:
        f.write("@echo off\necho Running install...\n")
        
    # 5. Regular code file
    code_data = """
    def main():
        print("Hello from AegisAI Trial")
    if __name__ == "__main__":
        main()
    """
    with open(os.path.join(TRIAL_DIR, "hello.py"), "w") as f:
        f.write(code_data)
        
    # 6. Temp file
    with open(os.path.join(TRIAL_DIR, "temp_cache.tmp"), "w") as f:
        f.write("temporary junk log data")

async def run_trial():
    # 1. Back up config.py
    config_path = os.path.join(backend_dir, "config.py")
    config_backup_path = os.path.join(backend_dir, "config.py.bak")
    shutil.copyfile(config_path, config_backup_path)
    
    try:
        # Overwrite config.py with trial scan path
        with open(config_path, "w") as f:
            f.write(f'SCAN_PATHS = [r"{TRIAL_DIR}"]\n')
            
        # Re-import / update SCAN_PATHS dynamically
        import importlib
        importlib.reload(config)
        main.SCAN_PATHS = [TRIAL_DIR]
        
        # Setup files
        setup_trial_files()
        
        # Reset database tables
        print("Initializing database tables...")
        create_tables()
        
        # Start scan
        print("Starting background scan via endpoint...")
        scan_response = await main.scan_and_save()
        task_id = scan_response["task_id"]
        print(f"Scan started. Task ID: {task_id}")
        
        # Poll status
        while True:
            status_info = main.scan_status(task_id)
            status = status_info["status"]
            processed = status_info["processed_files"]
            total = status_info["total_files"]
            print(f"Scan Status: {status} ({processed}/{total} files processed)")
            if status in ["completed", "failed"]:
                if status == "failed":
                    print(f"Scan failed with error: {status_info['error']}")
                break
            await asyncio.sleep(0.5)
            
        # Call endpoints to collect trial data with safe wrappers
        print("\nRetrieving trial analysis reports...")
        
        def safe_call(func, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return {"error": f"Endpoint call failed: {str(e)}"}

        async def safe_call_async(func, *args, **kwargs):
            try:
                return await asyncio.to_thread(func, *args, **kwargs)
            except Exception as e:
                return {"error": f"Endpoint call failed: {str(e)}"}
        
        storage_info = safe_call(main.storage_analysis)
        dup_info = safe_call(main.duplicates)
        cat_info = safe_call(main.storage_by_category)
        sec_info = safe_call(main.security_report)
        largest = safe_call(main.largest_files)
        advice_info = safe_call(main.ai_cleanup_advice)
        
        print("Running semantic search for 'credentials'...")
        sem_info = await safe_call_async(main.semantic_search, "credentials")
        
        print("Generating folder summary...")
        fold_summary = await safe_call_async(main.folder_summary, TRIAL_DIR)
        
        # Compile report
        report = {
            "trial_directory": TRIAL_DIR,
            "scan_status": status_info,
            "storage_analysis": storage_info,
            "duplicates": dup_info,
            "category_distribution": cat_info,
            "security_report": sec_info,
            "largest_files": largest,
            "ai_cleanup_advice": advice_info,
            "semantic_search_test": sem_info,
            "folder_summary": fold_summary
        }
        
        # Write json report to file
        report_path = os.path.join(backend_dir, "trial_report.json")
        with open(report_path, "w") as r_file:
            json.dump(report, r_file, indent=2)
            
        print(f"\nTrial completed successfully! JSON report saved to: {report_path}")
        
    finally:
        # Restore config.py
        if os.path.exists(config_backup_path):
            shutil.move(config_backup_path, config_path)
            print("Restored original config.py")
            
        # Clean up trial directory
        if os.path.exists(TRIAL_DIR):
            shutil.rmtree(TRIAL_DIR)
            print("Cleaned up trial files.")

if __name__ == "__main__":
    asyncio.run(run_trial())
