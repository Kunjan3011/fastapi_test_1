from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Response

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Users
from app.routers.auth import get_current_user

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
async def upload_profile_photo(db: db_dependency, user: user_dependency, file: UploadFile, username: str):
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
def view_profile_photo(db: db_dependency, user: user_dependency, username: str):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_user = db.query(Users).filter(user.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Enter your valid username")
    if not db_user.profile_picture:
        raise HTTPException(status_code=404, detail="Profile picture not found")
    return Response(content=db_user.profile_picture, media_type="image/png" or "image/jpeg")
