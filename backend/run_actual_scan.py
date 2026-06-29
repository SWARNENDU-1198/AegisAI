import sys
import os
import asyncio
import time
import json

# Add backend directory to path
backend_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)

import config
import main

async def run_actual_scan():
    print("AegisAI - Actual System Scan & Report")
    print("=====================================")
    print("Scan Paths Configured:")
    for p in config.SCAN_PATHS:
        print(f" - {p} (Exists: {os.path.exists(p)})")
    print()

    # Start scan
    print("Starting background filesystem crawl and analysis...")
    scan_response = await main.scan_and_save()
    task_id = scan_response["task_id"]
    print(f"Scan started. Task ID: {task_id}")
    
    # Poll status
    start_time = time.time()
    last_processed = -1
    while True:
        status_info = main.scan_status(task_id)
        status = status_info["status"]
        processed = status_info["processed_files"]
        total = status_info["total_files"]
        
        if processed != last_processed or status in ["completed", "failed"]:
            print(f"Scan Status: {status} ({processed}/{total} files processed, Elapsed: {int(time.time() - start_time)}s)")
            last_processed = processed
            
        if status in ["completed", "failed"]:
            if status == "failed":
                print(f"Scan failed with error: {status_info['error']}")
            break
        await asyncio.sleep(1.0)
        
    # Call endpoints to collect actual system reports
    print("\nRetrieving system analysis reports...")
    
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
    
    # Select first existing scan path for folder summary
    summary_path = None
    for p in config.SCAN_PATHS:
        if os.path.exists(p):
            summary_path = p
            break
            
    fold_summary = None
    if summary_path:
        print(f"Generating folder summary for: {summary_path}...")
        fold_summary = await safe_call_async(main.folder_summary, summary_path)
    
    # Compile report
    report = {
        "scan_status": status_info,
        "storage_analysis": storage_info,
        "duplicates": {
            "duplicate_groups": dup_info.get("duplicate_groups", 0),
            "duplicate_files": dup_info.get("duplicate_files", 0),
            "recoverable_space_bytes": dup_info.get("recoverable_space_bytes", 0),
            "duplicates_sample": dup_info.get("duplicates", [])[:5] # Limit sample
        } if isinstance(dup_info, dict) else dup_info,
        "category_distribution": cat_info,
        "security_report": sec_info,
        "largest_files": largest,
        "ai_cleanup_advice": advice_info,
        "folder_summary": fold_summary
    }
    
    # Write json report to file
    report_path = os.path.join(backend_dir, "actual_system_report.json")
    print(f"DEBUG: Resolving report_path to: {report_path}")
    with open(report_path, "w") as r_file:
        json.dump(report, r_file, indent=2)
        
    print(f"DEBUG: File exists immediately after write: {os.path.exists(report_path)}")
    if os.path.exists(report_path):
        print(f"DEBUG: Written file size: {os.path.getsize(report_path)} bytes")
        
    print(f"\nActual system scan completed! Report saved to: {report_path}")

if __name__ == "__main__":
    asyncio.run(run_actual_scan())
