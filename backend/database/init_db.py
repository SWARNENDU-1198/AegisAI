try:
    from .db import engine
    from .models import Base
except Exception:
    from database.db import engine
    from database.models import Base

def create_tables():
    Base.metadata.create_all(bind=engine)