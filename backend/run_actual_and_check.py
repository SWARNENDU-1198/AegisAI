import sys
import os
import asyncio

# Add backend directory to path
backend_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)

from database.db import SessionLocal
from database.models import FileRecord
import main

async def main_check():
    db = SessionLocal()
    print("Row count before scan:", db.query(FileRecord).count())
    db.close()
    
    # Run scan
    print("Running actual scan...")
    scan_response = await main.scan_and_save()
    task_id = scan_response["task_id"]
    
    # Poll status
    while True:
        status_info = main.scan_status(task_id)
        status = status_info["status"]
        if status in ["completed", "failed"]:
            print(f"Scan finished with status: {status}")
            break
        await asyncio.sleep(0.5)
        
    db = SessionLocal()
    print("Row count after scan:", db.query(FileRecord).count())
    db.close()

if __name__ == "__main__":
    asyncio.run(main_check())
