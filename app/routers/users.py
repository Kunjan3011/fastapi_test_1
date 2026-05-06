from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Response
from geopy.geocoders import Nominatim
from sqlalchemy.orm import Session
from starlette import status

from app.database import SessionLocal
from app.models import Users
from app.routers.auth import get_current_user
from app.schemas import UserUpdate

router = APIRouter(
    tags=['users'],
    prefix="/users"
)


def get_location_by_city(city: str):
    geolocator = Nominatim(user_agent="fastapi-location-tracker")
    location = geolocator.geocode(city)
    if location:
        return {
            "city": city,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "address": location.address
        }
    return {"city": city, "latitude": None, "longitude": None, "address": None}


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


@router.put("/update_profile_location/{username}", status_code=status.HTTP_204_NO_CONTENT)
def update_profile(db: db_dependency, user: user_dependency, username: str, user_update: UserUpdate):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    db_user = db.query(Users).filter(user.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not authenticated")
    geolocator = get_location_by_city(user_update.city)
    db_user.city = geolocator.get('city')
    db_user.latitude = geolocator.get('latitude')
    db_user.longitude = geolocator.get('longitude')
    db_user.address = geolocator.get('address')
    db.add(db_user)
    db.commit()
