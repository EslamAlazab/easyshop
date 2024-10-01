import os
from passlib.context import CryptContext
from models import User
from jose import jwt, JWTError
import datetime
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from typing import Annotated


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='user-api/token')

KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'


def authenticate_user(username, password, db):
    user = db.query(User).filter(User.username == username).first()
    if user and bcrypt_context.verify(password, user.password):
        return user
    return False


def gen_token(user_id, username, expires_delta):
    expires = datetime.datetime.now(datetime.UTC) + expires_delta
    encode = {'sub': username, 'id': user_id, 'exp': expires}
    return jwt.encode(encode, key=KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if not username or not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id}
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')


user_dependency = Annotated[User, Depends(get_current_user)]


def get_email_user(token: str):
    try:
        payload = jwt.decode(token, KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
