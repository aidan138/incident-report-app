from fastapi import APIRouter, Form, Depends, HTTPException
from app.config import settings
from app.core.prompts import build_prompt_flow
from app.services.twilio import send_sms
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.crud import crud

router = APIRouter()
twilio_number = settings.twilio_number
workflow_head, state_to_node = build_prompt_flow()


@router.post('/incident')
async def handle_incident_report(
    From: str = Form(...),
    Message: str = Form(...),
    To: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    
    curr_incident = await crud.get_incident_by_phone(db, From)
    if curr_incident:
        # Ask the next prompt
        curr_state = state_to_node[curr_incident.state]
    else:
        # Create a new incident in the db and continue
        curr_incident = await crud.create_incident(creator_phone=From)
        curr_state = workflow_head
    
    send_sms(To, From, curr_state.prompt)
    curr_state = curr_state.next
    # Update database table with next state
    curr_incident.status = curr_state.field_name
    await db.commit()
    await db.refresh()