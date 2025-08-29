from fastapi import FastAPI, Depends
from typing import Annotated 
from .db import engine, SessionLocal, Base, get_db
from sqlalchemy.orm import Session
from .routers import routes
# from contextlib import asynccontextmanager
# from . import db, models


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     async with db.engine.begin() as conn:
#         await conn.run_sync(db.Base.metadata.create_all())

app = FastAPI()
app.include_router(routes.router)

Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)] # Session for database

@app.get("/")
async def root() -> dict[str, str]:
    return {"Hello": "World"}