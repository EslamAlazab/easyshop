from fastapi import FastAPI
from database import engine
from models import Base
from users import users
from business import business, products
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(users.route)
app.include_router(business.router)
app.include_router(products.router)
