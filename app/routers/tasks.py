from time import gmtime, strftime

from fastapi import APIRouter, HTTPException
from starlette import status

from app.models import Tasks
from app.schemas import TaskView, TaskCreate
from app.utils.auth_utils import user_dependency
from app.utils.dependency_utils import db_dependency

router = APIRouter(
    tags=['tasks'],
    prefix='/tasks'
)


#create task for the user
@router.post("/create_task", status_code=status.HTTP_201_CREATED)
def create_task(db: db_dependency, user: user_dependency, task: TaskCreate):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    if task.completed.lower() not in ["yes", "no"]:
        raise HTTPException(status_code=406, detail="Task completed value is not valid! Enter Yes or No.")
    db_task = Tasks(
        name=task.name,
        description=task.description,
        user_id=user.id,
        completed=task.completed.lower(),
        priority=task.priority,
        created_at=strftime("%d %b %Y %H:%M:%S", gmtime()),
        deleted=False
    )
    db.add(db_task)
    db.commit()


#update the tasks according to the id you entered
@router.put("/update_task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_tasks(db: db_dependency, user: user_dependency, task: TaskCreate, task_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    if task.completed.lower() not in ["yes", "no"]:
        raise HTTPException(status_code=406, detail="Task completed value is not valid! Enter Yes or No.")
    db_task = db.query(Tasks).filter(Tasks.user_id == user.id).filter(
        Tasks.deleted == False).filter(Tasks.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.name = task.name
    db_task.description = task.description
    db_task.priority = task.priority
    db_task.completed = task.completed.lower()
    db_task.updated_at = strftime("%d %b %Y %H:%M:%S", gmtime())
    db.add(db_task)
    db.commit()


#view all your tasks
@router.get('/view_your_tasks', response_model=list[TaskView])
def view_your_tasks(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    tasks = db.query(Tasks).filter(Tasks.user_id == user.id).filter(Tasks.deleted == False).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="Tasks are not added yet")
    return tasks


#delete tasks by id
@router.delete('/delete_your_task/{task_id}')
def delete_your_task(db: db_dependency, user: user_dependency, task_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_task = db.query(Tasks).filter(Tasks.user_id == user.id).filter(Tasks.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.deleted = True
    db.add(db_task)
    db.commit()
