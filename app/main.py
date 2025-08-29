from fastapi import FastAPI
from app.routers import portal, sms
from app.core.exceptions import register_exceptions
from app.config import settings
# from contextlib import asynccontextmanager
# from . import db, models


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     async with db.engine.begin() as conn:
#         await conn.run_sync(db.Base.metadata.create_all())

app = FastAPI(title=settings.project_name)
app.include_router(portal.router, prefix="/portal")
app.include_router(sms.router, prefix="/sms")
register_exceptions(app=app)

@app.get("/")
async def root() -> dict[str, str]:
    return {"Hello": "World"}