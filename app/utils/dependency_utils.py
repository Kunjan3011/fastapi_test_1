from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal


#this which start the database for the endpoint to perform its query and close the database after completing it
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#database dependency for endpoints
db_dependency = Annotated[Session, Depends(get_db)]
