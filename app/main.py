from fastapi import FastAPI, Depends
from typing import Annotated 
from app.db import engine, SessionLocal, Base, get_db
from sqlalchemy.orm import Session
from app.routers import portal, sms
from app.core.exceptions import register_exceptions
# from contextlib import asynccontextmanager
# from . import db, models


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     async with db.engine.begin() as conn:
#         await conn.run_sync(db.Base.metadata.create_all())

app = FastAPI()
app.include_router(portal.router, prefix="/portal")
app.include_router(sms.router, prefix="/sms")

Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)] # Session for database
register_exceptions(app=app)

@app.get("/")
async def root() -> dict[str, str]:
    return {"Hello": "World"}