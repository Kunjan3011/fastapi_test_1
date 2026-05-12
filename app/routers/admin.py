from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import Response

from app.models import Tasks, Users, UserLogs

from app.schemas import UserView
from app.utils.auth_utils import user_dependency
from app.utils.dependency_utils import db_dependency

router = APIRouter(
    tags=['admin'],
    prefix='/admin'
)


#for admin to view the all users logs for login and register
@router.get("/user_logs")
def view_activity_logs(db: db_dependency, user: user_dependency):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="Admin privileges required!")
    db_logs = db.query(UserLogs).all()
    return db_logs


#for admin to view all the tasks of every user
@router.get('/view_all_users_tasks')
def read_all_tasks(db: db_dependency, user: user_dependency):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="Admin privileges required!")
    db_tasks = db.query(Tasks).all()
    return db_tasks


#for admin to view all the user present in the database
@router.get('/view_all_user', response_model=list[UserView])
def read_all_users(db: db_dependency, user: user_dependency):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="Admin privileges required!")
    db_users = db.query(Users).all()
    if not db_users:
        raise HTTPException(status_code=404, detail="Users not found")
    return db_users


#for admin to view the profile photo of any user according to their username
@router.get("/view_user_profile_photo/{username}")
def get_user_profile_photo(db: db_dependency, user: user_dependency, username: str):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="Admin privileges required!")
    db_user = db.query(Users).filter(Users.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.profile_picture:
        return Response(content=db_user.profile_picture, media_type="image/png" or "image/jpeg")
    return HTTPException(status_code=404, detail="This user has not uploaded their profile photo")


#for admin to delete any user
@router.delete("/delete_any_user/{username}")
def delete_any_username(db: db_dependency, user: user_dependency, username: str):
    if user is None or user.role != 'admin':
        raise HTTPException(status_code=401, detail="Admin privileges required!")
    db_user = db.query(Users).filter(Users.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully!"}
