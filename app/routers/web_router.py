from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models.incidents import Incident as ORMIncident
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/incident", tags=["Web Incident Review"])

@router.get("/{incident_id}/review")
async def review_incident(request: Request, incident_id: str, db: AsyncSession = Depends(get_db)):
    print("pk is", incident_id)
    incident = await db.get(ORMIncident, incident_id)
    print(incident.state)
    if not incident:
        return templates.TemplateResponse("review_incident.html", {"request": request, "error": "Incident not found"})

    return templates.TemplateResponse("review_incident.html", {"request": request, "incident": incident})
