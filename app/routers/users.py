from fastapi import APIRouter, HTTPException, UploadFile
from starlette.responses import RedirectResponse

from app.models import Users
from app.schemas import ViewProfilePhoto
from app.utils.auth_utils import user_dependency
from app.utils.cloudinary_utils import upload_to_cloudinary
from app.utils.dependency_utils import db_dependency

router = APIRouter(
    tags=['users'],
    prefix="/users"
)


#for all users to upload their photo
@router.post("/profile_photo")
async def upload_profile_photo(db: db_dependency, user: user_dependency, image: UploadFile):
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_user = db.query(Users).filter(Users.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    image_url = await upload_to_cloudinary(image)

    db_user.profile_picture = image_url
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Profile photo uploaded successfully", "image_url": image_url}


#for user to view their own profile photo
@router.get("/profile_photo",response_model=ViewProfilePhoto)
def view_profile_photo(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_user = db.query(Users).filter(user.username == Users.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not db_user.profile_picture:
        raise HTTPException(status_code=404, detail="Profile picture not found")
    return RedirectResponse(url=db_user.profile_picture)  #to redirecting response to cloudinary link of image


@router.delete("/profile_photo")
def delete_profile_photo(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_user = db.query(Users).filter(user.username == Users.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not db_user.profile_picture:
        raise HTTPException(status_code=404, detail="Profile picture not found")
    db_user.profile_picture = None
    db.add(db_user)
    db.commit()
    return {"message": "Profile photo deleted successfully!"}
