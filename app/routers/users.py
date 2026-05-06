import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Response
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


@router.post("/upload_photo/{username}")
async def upload_profile(db: db_dependency, user: user_dependency, file: UploadFile, username: str):
    max_size = 5 * 1024 * 1024
    content_types = ["image/png", "image/jpeg"]
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_user = db.query(Users).filter(user.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Enter your valid username")
    if file.content_type not in content_types:
        raise HTTPException(status_code=400, detail="File type not valid")
    file_data = await file.read(size=-1)
    if file.size > max_size:
        raise HTTPException(status_code=400, detail="File size not valid")
    db_user.profile_picture = file_data
    db_user.profile_file = file.filename
    db.add(db_user)
    db.commit()
    return {"message": "Photo uploaded successfully", "filename": file.filename, "size": file.size}


@router.get("/view_photo/{username}")
def view(db: db_dependency, user: user_dependency, username: str):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_user = db.query(Users).filter(user.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Enter your valid username")
    if not db_user.profile_picture:
        raise HTTPException(status_code=404, detail="Profile picture not found")
    return Response(content=db_user.profile_picture, media_type="image/png" or "image/jpeg")


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
    db_task = db.query(Tasks).filter(Tasks.user_id == user.id).filter(Tasks.id == id).filter(Tasks.deleted == "False").first()
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
