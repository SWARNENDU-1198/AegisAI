import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(os.path.dirname(db_dir), "aegisai.db")
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)