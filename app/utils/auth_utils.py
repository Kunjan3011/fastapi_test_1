import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import *

from jose import jwt, JWTError

from app.models import Users
from app.utils.dependency_utils import db_dependency

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGO = os.getenv("ALGO")
EXPIRES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


#create access token for user who login in so that it stays valid till expires time
def create_access_token(data: dict):
    encode = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(minutes=EXPIRES)
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGO)


#this is a dependency of auth which will fetch the current user for the endpoint to make user that user get their data properly
def get_current_user(db: db_dependency, access_token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=ALGO)
        username = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid access token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


user_dependency = Annotated[dict, Depends(get_current_user)]
