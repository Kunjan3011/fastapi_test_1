from datetime import *
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from app.database import SessionLocal
from app.models import Users
from app.schemas import UserCreate, Token

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
    db_user = Users(
        username=user.username,
        hashed_password=bcrypt_context.hash(user.password),
        role=user.role,
        city=user.city,
        ip=request.client.host
    )
    db.add(db_user)
    db.commit()


def create_access_token(data: dict):
    encode = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(minutes=EXPIRES)
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGO)


@router.post("/login", response_model=Token)
def login_for_access_token(db: db_dependency, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    db_user = db.query(Users).filter(Users.username == form.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail='Invalid Username')
    if not bcrypt_context.verify(form.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail='Authentication Failed')
    access_token = create_access_token(data={'sub': db_user.username})
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
