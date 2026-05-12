from datetime import *
from typing import Annotated
import os
import ipinfo
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from starlette import status

from app.models import Users, UserLogs

from app.schemas import UserCreate, Token
from app.utils.auth_utils import create_access_token
from app.utils.dependency_utils import db_dependency

load_dotenv()

token = os.getenv("token")


def get_location(ip_address: str):
    handler = ipinfo.getHandler(access_token=token)

    location = handler.getDetails(ip_address)

    if location:
        return {
            "city": location.city,
            "country": location.country,
            "location": location.loc
        }

    return {"city": None, "country": None, "location": None}


def get_client_ip(request: Request):
    forwarded = request.headers.get("x-forwarded-for")

    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host
    return ip


router = APIRouter(
    tags=['auth'],
    prefix='/auth'
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGO = os.getenv("ALGO")
EXPIRES = 30

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
def register_user(db: db_dependency, user: UserCreate, request: Request):
    repeated_username = db.query(Users).filter(Users.username == user.username).first()
    roles = ["user", "admin"]
    if repeated_username:
        raise HTTPException(status_code=406, detail="Username already exists! Try other username.")
    if user.role.lower() not in roles:
        raise HTTPException(status_code=406, detail="Enter valid role!")
    client_ip = get_client_ip(request)
    location_details = get_location(client_ip)
    db_user = Users(
        username=user.username,
        hashed_password=bcrypt_context.hash(user.password),
        role=user.role.lower(),
        city=location_details.get('city'),
        country=location_details.get('country'),
        location=location_details.get('location')

    )
    db.add(db_user)
    db.commit()
    db_log = UserLogs(
        username=db_user.username,
        ip=client_ip,
        location=location_details.get('location'),
        activity="register",
        activity_time=datetime.now(timezone.utc)
    )
    db.add(db_log)
    db.commit()
    return {"message": "User created successfully!"}


@router.post("/login", response_model=Token)
def login_for_access_token(db: db_dependency, form: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request):
    MAX_ATTEMPTS = 3
    TIME_LIMIT = 5
    # this is just for defining the time duration according to current time so that this duration get blocked if attempts fail
    time_window = datetime.now(timezone.utc) - timedelta(minutes=TIME_LIMIT)
    db_user = db.query(Users).filter(Users.username == form.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail='Invalid Username')
    client_ip = get_client_ip(request)
    recent_attempts = (
        db.query(UserLogs)
        .filter(
            UserLogs.username == form.username,
            UserLogs.ip == client_ip,
            UserLogs.activity == "login_failed",
            UserLogs.activity_time > time_window
            #this will satisfy till 3 attempts, after that the attempts will be 3 and this will return 3 and block the login till next 5 minutes
        )
        .count()
    )
    if recent_attempts >= MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many login requests")

    if not bcrypt_context.verify(form.password, db_user.hashed_password):
        failed_log = UserLogs(
            username=db_user.username,
            ip=client_ip,
            location=db_user.location,
            activity="login_failed",
            activity_time=datetime.now(timezone.utc)
        )
        db.add(failed_log)
        db.commit()
        raise HTTPException(status_code=401, detail="Authentication Failed")

    access_token = create_access_token(data={'sub': db_user.username})
    success_log = UserLogs(
        username=db_user.username,
        ip=client_ip,
        location=db_user.location,
        activity="login_success",
        activity_time=datetime.now(timezone.utc)
    )
    db.add(success_log)
    db.commit()
    return {"access_token": access_token, "token_type": "bearer"}
