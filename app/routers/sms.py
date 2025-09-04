from fastapi import APIRouter, Form, Depends, HTTPException
from app.config import settings
from app.core.prompts import build_prompt_flow
from app.services.twilio import send_sms
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.crud import crud
from app.models.incidents import Incident
from geopy.geocoders import Nominatim
import re

router = APIRouter()
twilio_number = settings.twilio_number
workflow_head, state_to_node = build_prompt_flow()
geolocator = Nominatim(user_agent='address_validator')
end_msg = "TERMINATE"
addr_pat = r"""
^
\s*                                                 
([\d\w\s.-]+(?:\s(?:Apt|Suite|\#)\s*\d+)?)          # street with optional unit
(?:,|\r?\n)\s*                                      # comma or newline separator
([\w\s.-]+)                                         # city
(?:,|\s)                                            # optional comma or space before region/state
([A-Z]{2}|[\w\s.-]+)?                               # US state or international region (optional)
\s*                                                 # optional spaces
(\d{5}(?:-\d{4})?|\w+)?                             # ZIP/postal code (US or international) optional
(?:\r?\n([\w\s]+))?                                 # optional country line
\s*$
"""
pattern = re.compile(addr_pat, re.VERBOSE)


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
        print("The current incident state is", curr_incident.state)
        next_message = await handle_message(db=db, incident=curr_incident, message=Body.strip())
    else:
        # Create a new incident in the db and continue
        curr_incident = await crud.create_incident(db=db, phone=From)
        next_message = workflow_head.prompt
    
    if next_message == end_msg:
        await crud.delete_incident(db, curr_incident)

    print(next_message)
    await send_sms(To, From, next_message)    


async def handle_message(db: AsyncSession, incident: Incident, message: str):
    curr_state = state_to_node[incident.state]
    valid_output, error_msg = None, None

    if incident.state == "start":
        valid_output, error_msg = parse_start(message)
    elif "phone" in incident.state:
        # Standard sequential data extraction
        valid_output, error_msg = parse_phone_number(message)
    elif "address" in incident.state:
        valid_output, error_msg = parse_address(message)
    elif incident.state == "summary":
        # For the initial text chat
        return
    elif incident.state == "follow_up":
        # After the initial text summary have ChatGPT ask follow ups for information it is unsure of
        return
    elif incident.state == "done":
        error_msg = "This report has already been concluded."
    
    else:
        valid_output = message
    
    if valid_output:
        # Update the database with the validated output
        if incident.state != "start":
            setattr(incident, curr_state.field_name, valid_output)
        incident.state = curr_state.next.field_name
        await db.commit()
        await db.refresh(incident)
        return curr_state.next.prompt
    else:
        # Simply return the error message without changing the updated state
        return error_msg


def parse_phone_number(phone_str: str) -> tuple[str | None, str | None]:
    phone_str = phone_str if phone_str.startswith("+") else "+1" + phone_str
    if phone_str[1:].isdigit() and 11 <= len(phone_str[1:]) < 14:
        return phone_str, None
    return "Please input a valid phone number As a single number (ex: (123) 1234-1234 would be 1231234123).", None

def parse_address(addr_str: str) -> tuple[str | None, str | None]:
    print(addr_str)
    if not re.match(pattern, addr_str):
        return None, "Please enter a valid address (ex. 123 Main St, Aliso Viejo, CA 92620)."
    
    location = geolocator.geocode(addr_str, timeout=5)
    if location:
        return location.address, None
    return None, "We couldn't locate that address. Please check for typos."

def parse_start(start_msg: str) -> tuple[str | None, str | None]:
    if start_msg == "Y":
        # Valid message
        return start_msg, None
    
    elif start_msg == "n":
        # Must terminate the database instance
        None, end_msg

    return None, "Reply 'Y' to proceed with the incident report or 'n' to cancel"
