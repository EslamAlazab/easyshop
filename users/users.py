from fastapi import APIRouter, status, BackgroundTasks, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from database import db_dependency
from models import User
from .email_verification import email_verify, templates
from .auth import authenticate_user, gen_token, user_dependency, get_email_user
from datetime import timedelta
from .schemas import UserRequest, Token
from typing import Annotated

route = APIRouter(prefix='/user-api', tags=['user'])


@route.get('/all')
async def get_all_users(db: db_dependency):
    return db.query(User).all()


@route.post('/signup', status_code=status.HTTP_201_CREATED)
async def register(user: UserRequest, db: db_dependency):
    user = User(**user.model_dump())
    db.add(user)
    db.commit()


@route.post('/token', response_model=Token)
async def login(user_form: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(user_form.username, user_form.password, db)
    if not user:
        raise HTTPException(
            status_code=401, detail='Could not athenticate the user.')
    token = gen_token(user.user_id, user.username, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}


@route.post("/verify-email")
async def email_verification(user: user_dependency, request: Request, background_tasks: BackgroundTasks, db: db_dependency):
    background_tasks.add_task(email_verify, user, request, db)
    return {"message": "Email has been sent in the background"}


@route.get("/verify-email/", response_class=HTMLResponse)
async def email_verification(token: str, request: Request, db: db_dependency):
    user = get_email_user(token)
    if not user:
        raise HTTPException(
            status_code=401, detail='Could not athenticate the user.')
    user = db.query(User).filter(User.user_id == user.get('id')).first()
    user.is_verified = True
    db.commit()
    return templates.TemplateResponse(request, 'verified.html', {'username': user.username})
