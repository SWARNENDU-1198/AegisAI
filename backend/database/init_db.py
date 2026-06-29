try:
    from .db import engine
    from .models import Base
except Exception:
    from database.db import engine
    from database.models import Base

from sqlalchemy import text

def create_tables():
    Base.metadata.create_all(bind=engine)
    # Check if category column exists, if not, add it
    with engine.connect() as conn:
        try:
            cursor = conn.execute(text("PRAGMA table_info(files)"))
            columns = [row[1] for row in cursor.fetchall()]
            if "category" not in columns:
                conn.execute(text("ALTER TABLE files ADD COLUMN category VARCHAR"))
                conn.commit()
            if "meta_data" not in columns:
                conn.execute(text("ALTER TABLE files ADD COLUMN meta_data TEXT"))
                conn.commit()
            if "vector_embedding" not in columns:
                conn.execute(text("ALTER TABLE files ADD COLUMN vector_embedding TEXT"))
                conn.commit()
        except Exception:
            pass
