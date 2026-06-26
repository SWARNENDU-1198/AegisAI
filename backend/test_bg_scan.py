import subprocess
import time
import urllib.request
import urllib.error
import json
import logging
import sys
import os
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_integration_test():
    # 0. Setup temporary scan directory and configuration
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_scan_dir"))
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a few small files to scan
    for i in range(5):
        file_path = os.path.join(test_dir, f"test_file_{i}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Sample content for file {i} to calculate hash.")
            
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "config.py"))
    config_backup_path = config_path + ".bak"
    
    # Backup original config if it exists
    has_config_backup = False
    if os.path.exists(config_path):
        shutil.copy2(config_path, config_backup_path)
        has_config_backup = True
        
    try:
        # Write test configuration
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(f"SCAN_PATHS = [r'{test_dir}']\n")
            
        # 1. Start uvicorn in a subprocess
        logger.info("Starting uvicorn on port 8099...")
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--port", "8099", "--log-level", "warning"],
            cwd="backend"
        )
        
        # Wait for server to start
        time.sleep(6)
        
        # Check if process is still running
        poll = proc.poll()
        if poll is not None:
            logger.error("Uvicorn process terminated unexpectedly with code: %s", poll)
            sys.exit(1)
            
        try:
            # Check home endpoint
            logger.info("Verifying server is running...")
            req = urllib.request.Request("http://127.0.0.1:8099/")
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                assert data["message"] == "AegisAI Running"
                
            # Trigger background scan
            logger.info("Triggering scan-and-save...")
            req_scan = urllib.request.Request("http://127.0.0.1:8099/scan-and-save")
            with urllib.request.urlopen(req_scan) as resp:
                scan_data = json.loads(resp.read().decode())
                assert scan_data["message"] == "Scan started in background"
                assert "task_id" in scan_data
                task_id = scan_data["task_id"]
                
            logger.info("Scan started with task_id: %s", task_id)
            
            # Test concurrent scan (expecting 409 Conflict)
            try:
                logger.info("Testing concurrent scan block...")
                req_concurrent = urllib.request.Request("http://127.0.0.1:8099/scan-and-save")
                urllib.request.urlopen(req_concurrent)
                assert False, "Concurrent scan should fail with 409"
            except urllib.error.HTTPError as e:
                assert e.code == 409
                error_data = json.loads(e.read().decode())
                assert "Scan already in progress" in error_data["detail"]["message"]
                logger.info("Concurrent scan block verified successfully.")
                
            # Poll status until complete
            for _ in range(15):
                time.sleep(1)
                req_status = urllib.request.Request(f"http://127.0.0.1:8099/scan-status/{task_id}")
                with urllib.request.urlopen(req_status) as resp:
                    status_data = json.loads(resp.read().decode())
                    logger.info(
                        "Status: %s | Progress: %d%% (%d/%d) | Current file: %s | Elapsed: %ds",
                        status_data["status"],
                        status_data["progress_percent"],
                        status_data["processed_files"],
                        status_data["total_files"],
                        status_data["current_file"],
                        status_data["elapsed_seconds"]
                    )
                    if status_data["status"] in ["completed", "failed"]:
                        assert status_data["status"] == "completed", f"Scan failed: {status_data['error']}"
                        break
            else:
                assert False, "Scan timed out after 15 seconds"
                
            logger.info("Background scan and status tracking verified successfully!")
            
        finally:
            logger.info("Stopping uvicorn server...")
            proc.terminate()
            proc.wait()
            
    finally:
        # Restore configuration
        if has_config_backup:
            if os.path.exists(config_backup_path):
                shutil.move(config_backup_path, config_path)
        elif os.path.exists(config_path):
            os.remove(config_path)
            
        # Clean up temporary scan directory
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

if __name__ == "__main__":
    run_integration_test()
