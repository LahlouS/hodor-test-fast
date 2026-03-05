from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

DB_CONNEXION_URL = settings.POSTGRES_DB_URL
# The `connect_args` parameter is needed only for SQLite.
engine = create_engine(
	DB_CONNEXION_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
