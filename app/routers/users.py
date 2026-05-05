import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.database import SessionLocal
from app.models import Tasks, Users
from app.routers.auth import get_current_user
from app.schemas import TaskCreate, TaskView

router = APIRouter(
    tags=['users'],
    prefix="/users"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/create_task", status_code=status.HTTP_201_CREATED)
def create_task(db: db_dependency, user: user_dependency, task: TaskCreate):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_task = Tasks(
        name=task.name,
        description=task.description,
        user_id=user.id,
        created_at=str(datetime.date.today().strftime("%d/%m/%Y")),
        deleted="False"
    )
    db.add(db_task)
    db.commit()


@router.put("/update_task/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_tasks(db: db_dependency, user: user_dependency, id: int, task: TaskCreate):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_task = db.query(Tasks).filter(Tasks.user_id == user.id).filter(Tasks.id == id).filter(Tasks.deleted=="False").first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.name = task.name
    db_task.description = task.description
    db_task.updated_at = str(datetime.date.today().strftime("%d/%m/%Y"))
    db.add(db_task)
    db.commit()


@router.get('/view_your_tasks', response_model=TaskView)
def view_your_tasks(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    tasks = db.query(Tasks).filter(Tasks.user_id == user.id).filter(Tasks.deleted == "False").first()
    if not tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks


@router.delete('/delete_your_task/{id}')
def delete_your_task(db: db_dependency, user: user_dependency, id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_task = db.query(Tasks).filter(Tasks.user_id == user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.deleted = "True"
    db.add(db_task)
    db.commit()


