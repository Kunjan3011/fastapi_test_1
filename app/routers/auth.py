import datetime
from datetime import *
from typing import Annotated

import ipinfo
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from app.database import SessionLocal
from app.models import Users, UserLogs
from app.schemas import UserCreate, Token

token = '97ffc883be38c7'


def get_location():
    handler = ipinfo.getHandler(access_token=token)
    location = handler.getDetails()
    if location:
        return {
            "city": location.city,
            "country": location.country_name,
            "location": location.loc
        }
    return {"city": None, "country": None, "location": None}


router = APIRouter(
    tags=['auth'],
    prefix='/auth'
)

SECRET_KEY = '2721ccef1f38045ee463c7c3daabc40197d8479421345bbd3e13d9ef866d735e'
ALGO = 'HS256'
EXPIRES = 30


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
def register_user(db: db_dependency, user: UserCreate, request: Request):
    location_details = get_location()
    db_user = Users(
        username=user.username,
        hashed_password=bcrypt_context.hash(user.password),
        role=user.role,
        city=location_details.get('city'),
        country=location_details.get('country'),
        location=location_details.get('location')

    )
    db.add(db_user)
    db.commit()
    db_log = UserLogs(
        username=db_user.username,
        ip=request.client.host,
        location=location_details.get('location'),
        activity="register",
        activity_time=datetime.now(timezone.utc)
    )
    db.add(db_log)
    db.commit()


def create_access_token(data: dict):
    encode = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(minutes=EXPIRES)
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGO)


@router.post("/login", response_model=Token)
def login_for_access_token(db: db_dependency, form: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request):
    db_user = db.query(Users).filter(Users.username == form.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail='Invalid Username')
    if not bcrypt_context.verify(form.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail='Authentication Failed')
    access_token = create_access_token(data={'sub': db_user.username})
    db_log = UserLogs(
        username=db_user.username,
        ip=request.client.host,
        location=db_user.location,
        activity="login",
        activity_time=datetime.now(timezone.utc)
    )
    db.add(db_log)
    db.commit()
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(db: db_dependency, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGO)
        username = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
