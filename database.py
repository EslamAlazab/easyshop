from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends
from typing import Annotated

engine = create_engine('sqlite:///ecom.db')
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close


db_dependency = Annotated[Session, Depends(get_db)]
