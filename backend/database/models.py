from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import BigInteger

from sqlalchemy.orm import declarative_base

Base = declarative_base()

class FileRecord(Base):

    __tablename__ = "files"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    path = Column(String, unique=True)

    size = Column(BigInteger)

    extension = Column(String)

    hash = Column(String)