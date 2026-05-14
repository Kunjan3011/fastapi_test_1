from fastapi import APIRouter, HTTPException
from starlette import status

from app.models import Tasks, Users, UserLogs
from app.schemas import UserView
from app.utils.auth_utils import user_dependency
from app.utils.dependency_utils import db_dependency

router = APIRouter(
    tags=['admin'],
    prefix='/admin'
)


#for admin to view the all users logs for login and register
@router.get("/users/logs", status_code=status.HTTP_200_OK)
def view_activity_logs(db: db_dependency, user: user_dependency):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="Admin privileges required!")
    db_logs = db.query(UserLogs).all()
    return db_logs


#for admin to view all the tasks of every user
@router.get('/users/tasks', status_code=status.HTTP_200_OK)
def read_all_tasks(db: db_dependency, user: user_dependency):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="Admin privileges required!")
    db_tasks = db.query(Tasks).all()
    return db_tasks


#for admin to view all the user present in the database
@router.get('/users', response_model=list[UserView], status_code=status.HTTP_200_OK)
def read_all_users(db: db_dependency, user: user_dependency):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="Admin privileges required!")
    db_users = db.query(Users).all()
    if not db_users:
        raise HTTPException(status_code=404, detail="Users not found")
    return db_users


#for admin to view the profile photo of any user according to their username
@router.get("/users/{username}/profile_photo", status_code=status.HTTP_200_OK)
def get_user_profile_photo(db: db_dependency, user: user_dependency, username: str):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="Admin privileges required!")
    db_user = db.query(Users).filter(Users.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")
    if not db_user.profile_picture:
        raise HTTPException(status_code=404, detail="Profile photo not available!")
    return {"profile_picture_url": db_user.profile_picture}


#for admin to delete any user
@router.delete("/users/{username}", status_code=status.HTTP_200_OK)
def delete_any_username(db: db_dependency, user: user_dependency, username: str):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="Admin privileges required!")
    db_user = db.query(Users).filter(Users.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")
    db.delete(db_user)
    db.commit()
    return {"message": f"User {username} deleted successfully!",
            "success": True}
