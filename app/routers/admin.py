from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import Response

from app.database import SessionLocal
from app.models import Tasks, Users
from app.routers.auth import get_current_user
from app.schemas import UserView

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


@router.get('/view_all_user', response_model=list[UserView])
def read_all_users(db: db_dependency, user: user_dependency):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_users = db.query(Users).all()
    return db_users


@router.get("/view_user_profile_photo/{username}")
def get_user_profile_photo(db: db_dependency, user: user_dependency, username: str):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_user = db.query(Users).filter(Users.username == username).first()
    if db_user.profile_picture:
        return Response(content=db_user.profile_picture, media_type="image/png" or "image/jpeg")
    return {"message": "This user has not uploaded their profile photo"}


@router.delete("/delete_any_user/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_any_username(db: db_dependency, user: user_dependency, username: str):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_user = db.query(Users).filter(Users.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
