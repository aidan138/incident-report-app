from fastapi import APIRouter, Form, Depends, HTTPException
from app.config import settings
from app.core.prompts import build_prompt_flow
from app.services.twilio import send_sms
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.crud import crud
from app.models.incidents import Incident

router = APIRouter()
twilio_number = settings.twilio_number
workflow_head, state_to_node = build_prompt_flow()
addr_reqs = [()]

@router.post('/incident')
async def handle_incident_report(
    From: str = Form(...),
    Body: str = Form(...),
    To: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    
    curr_incident = await crud.get_incident_by_phone(db, From)
    if curr_incident:
        # Ask the next prompt
        next_message, curr_state = await handle_message(incident=curr_incident, message=Body)
    else:
        # Create a new incident in the db and continue
        curr_incident = await crud.create_incident(db=db, phone=From)
        curr_state = workflow_head
        next_message = curr_state.prompt
    print(next_message)
    await send_sms(To, From, next_message)
    print("The current incident is {}")
    # Update database table with next state
    if curr_state:
        print("Previous status", curr_incident.state)
        curr_incident.state = curr_state.next.field_name  # update the actual 'state'
        print("Current status", curr_incident.state)
        await db.commit()
        await db.refresh(curr_incident)


async def handle_message(incident: Incident, message: str):
    curr_state = state_to_node[incident.state]
    if incident.state == "summary":
        # For the initial text chat
        return
    elif incident.state == "follow_up":
        # After the initial text summary have ChatGPT ask follow ups for information it is unsure of
        return
    elif incident.state == "confirmation":
        # When the database schema is fully filled out
        return
    elif incident.state == "done":
        return "This report has already been concluded"
    elif "confirm_phone" in incident.state:
        # Standard sequential data extraction
        msg = parse_phone_number(message)
        return (msg, curr_state) if msg else ("Please input a valid phone number As a single number (ex: (123) 1234-1234 would be 1231234123)", None)
    else:
        return curr_state.prompt, curr_state

def parse_phone_number(phone_str: str) -> str | None:
    phone_str = phone_str.strip()
    phone_str = phone_str if phone_str.startswith("+") else "+1" + phone_str
    if phone_str[1:].isdigit() and 11 <= len(phone_str[1:]) < 14:
        return phone_str


    