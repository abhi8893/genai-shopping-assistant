from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from core.config import settings

DATABASE_URL = f"sqlite:///{settings.db_name}.db"

engine = create_engine(DATABASE_URL)

Base = declarative_base()
