from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models.incidents import Incident as ORMIncident
from fastapi.templating import Jinja2Templates
from app.services.pdf import email_pdf_bytes, generate_pdf_bytes
from app.schemas.incident_schemas import TypeOfIncident, TypeofInjury
from app.config import settings
from datetime import time, date, datetime

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/incident", tags=["Web Incident Review"])

@router.get("/{incident_id}/review")
async def review_incident(request: Request, incident_id: str, db: AsyncSession = Depends(get_db)):
    print("pk is", incident_id)
    incident = await db.get(ORMIncident, incident_id)
    print(incident.state)
    if not incident:
        return templates.TemplateResponse("review_incident.html", {"request": request, "error": "Incident not found"})

    return templates.TemplateResponse("review_incident.html", {"request": request, "incident": incident, "TypeOfIncident": TypeOfIncident, "TypeOfInjury": TypeofInjury})

@router.post("/{incident_id}/confirm")
async def confirm_incident(request: Request, incident_id: str, db: AsyncSession = Depends(get_db)):
    form = await request.form()
    form_data = dict(form)

    incident = await db.get(ORMIncident, incident_id)
    if not incident:
        return templates.TemplateResponse("review_incident.html", {"request": request, "error": "Incident not found"})
    
    if incident.state in {'sending','done'}:
        return {'status': 'noop', 'message': f'Incident is already {incident.state}'}
    
    for field, data in form_data.items():
        if not hasattr(incident, field):
            continue
        prev_type = type(getattr(incident, field))
        if prev_type is time and type(data) is str:
            print("The time data is ", data )
            data = datetime.strptime(data, '%H:%M:%S').time()
            print("The converted time data is", data.strftime('%I:%M%p'))
        elif prev_type is date and type(data) is str:
            data = datetime.strptime(data, "%Y-%m-%d").date()
            print("The converted date is", data.strftime("%m/%d/%Y"))
        
        setattr(incident, field, data)
    
    # Update database and incident with confirmed data
    incident.state = 'sending'
    await db.commit()
    await db.refresh(incident)

    pdf_bytes = generate_pdf_bytes(incident)
    
    try:
        await email_pdf_bytes(
            recipient=settings.mail_from,
            subject=f'Incident #{incident.pk}',
            body=f'Incident report for incident #{incident.pk}',
            filename=f'Incident{incident.pk}.pdf',
            pdf_bytes=pdf_bytes,
        )

        incident.state = 'done'
        await db.commit()
        return {"status": "ok", "message": "Incident confirmed and sent"}
    
    except Exception as exc:
        incident.state = 'error'
        await db.commit()
        raise

