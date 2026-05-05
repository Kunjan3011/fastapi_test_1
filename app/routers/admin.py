from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Tasks, Users
from app.routers.auth import get_current_user

router = APIRouter(
    tags=['admin'],
    prefix='/admin'
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/view_all_users_tasks')
def read_all_tasks(db: db_dependency, user: user_dependency):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_tasks = db.query(Tasks).all()
    return db_tasks


@router.get('/view_all_user')
def read_all_users(db: db_dependency, user: user_dependency):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_users = db.query(Users).all()
    return db_users
