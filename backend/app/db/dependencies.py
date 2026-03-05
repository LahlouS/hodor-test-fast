from .database import SessionLocal
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session


# Dependency
def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

db_dependency = Annotated[Session, Depends(get_db)]