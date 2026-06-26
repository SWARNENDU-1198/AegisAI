import logging
from database.init_db import create_tables
from database.db import SessionLocal
from database.models import FileRecord
from services.file_service import save_files

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_save_files():
    # 1. Initialize DB tables
    create_tables()
    
    db = SessionLocal()
    # Cleanup any existing test records if they exist
    db.query(FileRecord).filter(FileRecord.path.like("%test_dummy_%")).delete(synchronize_session=False)
    db.commit()
    
    # 2. Get initial count
    initial_count = db.query(FileRecord).count()
    logger.info("Initial record count: %d", initial_count)
    
    # 3. Prepare test files list
    test_files = [
        {
            "name": "dummy1.txt",
            "path": "C:\\test_dummy_1.txt",
            "size": 1024,
            "extension": ".txt",
            "hash": "hash1"
        },
        {
            "name": "dummy2.txt",
            "path": "C:\\test_dummy_2.txt",
            "size": 2048,
            "extension": ".txt",
            "hash": "hash2"
        },
        {
            "name": "dummy1_duplicate.txt",
            "path": "C:\\test_dummy_1.txt", # Duplicate path
            "size": 1024,
            "extension": ".txt",
            "hash": "hash1"
        }
    ]
    
    # 4. Save files (should insert 2 unique records)
    logger.info("Saving initial batch of files...")
    save_files(test_files)
    
    # 5. Verify database count
    count_after_first_save = db.query(FileRecord).count()
    logger.info("Record count after first save: %d", count_after_first_save)
    assert count_after_first_save == initial_count + 2, "Should have inserted exactly 2 unique records."
    
    # 6. Try saving again with same list (should insert 0 new records)
    logger.info("Saving duplicate batch of files...")
    save_files(test_files)
    
    count_after_second_save = db.query(FileRecord).count()
    logger.info("Record count after second save: %d", count_after_second_save)
    assert count_after_second_save == count_after_first_save, "Should not insert duplicate records."
    
    # 7. Add a new file record and save
    new_file = [
        {
            "name": "dummy3.txt",
            "path": "C:\\test_dummy_3.txt",
            "size": 512,
            "extension": ".txt",
            "hash": "hash3"
        }
    ]
    logger.info("Saving a new unique file...")
    save_files(new_file)
    
    count_after_third_save = db.query(FileRecord).count()
    logger.info("Record count after third save: %d", count_after_third_save)
    assert count_after_third_save == count_after_second_save + 1, "Should have inserted 1 new record."
    
    # 8. Clean up test records
    logger.info("Cleaning up test dummy records...")
    db.query(FileRecord).filter(FileRecord.path.like("%test_dummy_%")).delete(synchronize_session=False)
    db.commit()
    db.close()
    
    logger.info("All DB save tests passed successfully!")

if __name__ == "__main__":
    test_save_files()
