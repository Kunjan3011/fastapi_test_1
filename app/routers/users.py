from fastapi import APIRouter, HTTPException, UploadFile, Response

from app.models import Users
from app.utils.auth_utils import user_dependency
from app.utils.dependency_utils import db_dependency

router = APIRouter(
    tags=['users'],
    prefix="/users"
)


#for all users to upload their photo
@router.post("/upload_profile_photo")
async def upload_profile_photo(db: db_dependency, user: user_dependency, file: UploadFile):
    max_size = 5 * 1024 * 1024
    content_types = ["image/png", "image/jpeg"]
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_user = db.query(Users).filter(user.username == Users.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if file.content_type not in content_types:
        raise HTTPException(status_code=415, detail="File type not valid")
    file_data = await file.read(size=-1)
    if file.size > max_size:
        raise HTTPException(status_code=400, detail="File size not valid")
    db_user.profile_picture = file_data
    db_user.profile_file = file.filename
    db.add(db_user)
    db.commit()
    return {"message": "Photo uploaded successfully", "filename": file.filename}


#for user to view their own profile photo
@router.get("/view_profile_photo")
def view_profile_photo(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_user = db.query(Users).filter(user.username == Users.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not db_user.profile_picture:
        raise HTTPException(status_code=404, detail="Profile picture not found")
    return Response(content=db_user.profile_picture, media_type="image/png" or "image/jpeg")
