from fastapi import APIRouter, Form, Depends, HTTPException
from app.config import settings
from app.core.prompts import build_prompt_flow
from app.services.twilio import send_sms
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.crud import crud
from app.schemas import schemas
from app.models.incidents import Incident
from geopy.geocoders import Nominatim
import re
import logging
from app.services.gpt import extract_incident_info, generate_incident_followups

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
date_lens = (2,2,4)
fatal_server_response = "Incident reporting service currently down. Please perform handwritten incident reporting."


@router.post('/incident')
async def handle_incident_report(
    From: str = Form(...),
    Body: str = Form(...),
    To: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    
    curr_incident = await crud.get_incident_by_phone(db, From)
    if not curr_incident:
        # Create a new incident in the db and continue
        curr_incident = await crud.create_incident(db=db, phone=From)
        next_message = workflow_head.prompt
    elif curr_incident.state == "incident_summary":
        try:
            next_message = await handle_summary(db, curr_incident, Body)
        except HTTPException as e:
            logging.fatal(f"Unable to extract incident summary: {e}.")
            raise e
        finally:
            send_sms(From, To, fatal_server_response)

    elif curr_incident.state == "follow-up":
        try:
            next_message = await handle_follow_up(db, curr_incident, Body)
        except HTTPException as e:
            logging.fatal(f"Unable to ask follow-ups to complete incident reporst: {e}")
            raise e
        finally:
            send_sms(From, To, fatal_server_response)
    else:
        # Ask the next prompt
        logging.info("The current incident state is", curr_incident.state)
        next_message = await handle_serial_message(db=db, incident=curr_incident, message=Body.strip())
    
    if next_message == end_msg:
        await crud.delete_incident(db, curr_incident)
    else:
        logging.info(next_message)
        await send_sms(To, From, next_message)    


async def handle_serial_message(db: AsyncSession, incident: Incident, message: str):
    curr_state = state_to_node[incident.state]
    valid_output, error_msg = None, None

    if incident.state == "start":
        valid_output, error_msg = parse_start(message)
    elif "phone" in incident.state:
        # Standard sequential data extraction
        valid_output, error_msg = parse_phone_number(message)
    elif "address" in incident.state:
        valid_output, error_msg = parse_address(message)
    elif "date" in incident.state:
        valid_output, error_msg = parse_date(message)
    elif "time" in incident.state:
        valid_output, error_msg = parse_time(message)
    elif incident.state == "witness" and message.upper() == "NA":
        # Need to skip the next field
        valid_output = "NA"
        curr_state = curr_state.next
    elif incident.state == "done":
        # TODO Handle the end of message flows gracefully to allow same lifeguard to file multiple reports
        error_msg = "This report has already been concluded."
    else:
        # Handles names
        valid_output = message.capitalize()
    
    if valid_output:
        # Update the database with the validated output
        if incident.state != "start" or valid_output != 'NA':
            setattr(incident, curr_state.field_name, valid_output)
        incident.state = curr_state.next.field_name
        await db.commit()
        await db.refresh(incident)
        return curr_state.next.prompt
    else:
        # Simply return the error message without changing the updated state
        return error_msg

async def handle_summary(db, incident, message):
    # Set the incidents summary to be the message
    incident.summary = message
    incident_summary = await extract_incident_info(model=settings.openai_model, content=message)
    logging.info(f"Incident orm model before updating {incident}")
    await crud.update_incident_fields(db=db, incident_pk=incident.pk, fields_to_values=incident_summary.model_dump() | dict(incident_summary=message))
    await db.refresh(incident)
    logging.info(f"Incident orm model after updating {incident}")
    missing_fields = schemas.Incident.model_validate(incident).missing_fields
    logging.info(f"Found the following missing fields from summary: {missing_fields}")
    follow_ups = await generate_incident_followups(model=settings.openai_model, missing_fields=missing_fields)
    logging.info(f"Generated the follow-ups: {follow_ups}")


def handle_follow_up(db: AsyncSession, incident: Incident):
    pass


def parse_phone_number(phone_str: str) -> tuple[str | None, str | None]:
    phone_str = phone_str if phone_str.startswith("+") else "+1" + phone_str
    if phone_str[1:].isdigit() and 11 <= len(phone_str[1:]) < 14:
        return phone_str, None
    return None, "Please input a valid phone number As a single number (ex: (123) 1234-1234 would be 1231234123)."

def parse_date(date_str: str) -> tuple[str | None, str | None]:
    #TODO more robust handling ensuring valid dates and times
    date_list = date_str.split("/")
    if len(date_list) == 3:
        valid_output, error_msg = date_str, None
        for act_len, exp_len in zip([len(date) for date in date_list], date_lens):
            if act_len != exp_len:
                valid_output, error_msg = None, "Please ensure you entered a valid date in the form MM/DD/YYYY"
                break
    else:
        valid_output, error_msg = None, "Please ensure you entered a valid date in the form MM/DD/YYYY"
    return valid_output, error_msg
    
def parse_time(time_str) -> tuple[str | None, str | None]:
    time_list = time_str.split(":")
    if len(time_list) == 2 and len(time_list[0]) == 2 and len(time_list[1]) == 4:
        hours, minutes_m = time_list
        minutes, am_o_pm = minutes_m[:2], minutes_m[2:].lower()
        
        if 12 < int(hours) or int(hours) <= 0 or int(minutes) < 0 or int(minutes) >= 60 or\
        (am_o_pm != 'am' and am_o_pm != 'pm'):
            valid_output, error_msg = None, "Please enter a valid time in the form HH:MMam/pm (ex: 12:30pm)"
        else:
            valid_output, error_msg = time_str[:-2] + am_o_pm, None # Unifies the am/pm to be lower case
    else:
        valid_output, error_msg = None, "Please enter a valid time in the form HH:MMam/pm (ex: 12:30pm)"
    return valid_output, error_msg

def parse_address(addr_str: str) -> tuple[str | None, str | None]:
    logging.info(addr_str)
    # if not re.match(pattern, addr_str):
    #     return None, "Please enter a valid address (ex. 123 Main St, Aliso Viejo, CA 92620)."
    
    location = geolocator.geocode(addr_str, timeout=5)
    if location:
        return location.address, None
    return None, "We couldn't locate that address. Please check for typos."

def parse_start(start_msg: str) -> tuple[str | None, str | None]:
    logging.info(f"The message in parse start {start_msg}")
    if start_msg == "Y":
        # Valid message
        return start_msg, None
    elif start_msg == "n":
        # Must terminate the database instance
        return None, end_msg

    return None, "Reply 'Y' to proceed with the incident report or 'n' to cancel"
