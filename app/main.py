import os
from fastapi import FastAPI
from app.routers import portal, sms, web_router
from app.core.exceptions import register_exceptions
from app.config import settings
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

app = FastAPI(title=settings.project_name)
app.include_router(portal.router, prefix="/portal")
app.include_router(sms.router, prefix="/sms")
app.include_router(web_router.router)

register_exceptions(app=app)

@app.get("/")
async def root() -> dict[str, str]:
    return {"Hello": "World"}