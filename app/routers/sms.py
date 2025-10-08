from fastapi import APIRouter, Form, Depends, HTTPException
from app.config import settings
from app.core.prompts import build_prompt_flow
from app.services.twilio import send_sms
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.crud import crud
from app.schemas import incident_schemas
from app.models.incidents import Incident
from geopy.geocoders import Nominatim
import logging
from app.services.gpt import extract_incident_info, generate_incident_followups
from datetime import datetime
import re
import unicodedata
from rapidfuzz import fuzz
import jellyfish

router = APIRouter()
twilio_number = settings.twilio_number
workflow_head, state_to_node = build_prompt_flow()
geolocator = Nominatim(user_agent='address_validator')
skip_msg = "SKIP"
end_msg = "TERMINATE"
date_lens = (2,2,4)
fatal_server_response = "Incident reporting service currently down. Please perform handwritten incident reporting."
ROOT_URL = settings.root_url

ABBREV = {
    "&":" and ", "ctr":"center", "ct":"court", "co":"company",
    "st":"street", "ste":"suite", "blvd":"boulevard", "ave":"avenue",
    "hosp":"hospital", "med":"medical"
}
DROP_TAILS = {"pool"}
MATCH = 0.80

loc_to_id, loc_to_adr = crud.fetch_regions_to_locations_from_db(get_db())


@router.post('/incident')
async def handle_incident_report(
    From: str = Form(...),
    Body: str = Form(...),
    To: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    
    curr_incident = await crud.get_incident_by_phone(db, From)
    Body = Body.strip()
    if not curr_incident:
        # Create a new incident in the db and continue
        curr_incident = await crud.create_incident(db=db, phone=From)
        next_message = workflow_head.prompt

    elif curr_incident.followups:
        try:
            next_message = await handle_follow_up(db, curr_incident, Body)
        except HTTPException as e:
            logging.fatal(f"Unable to ask follow-ups to complete incident reporst: {e}")
            await send_sms(From, To, fatal_server_response)
            raise e

    elif curr_incident.state == "incident_summary":
        try:
            next_message = await handle_summary(db, curr_incident, Body)
        except HTTPException as e:
            logging.fatal(f"Unable to extract incident summary: {e}.")
            await send_sms(From, To, fatal_server_response)
            raise e

    else:
        # Ask the next prompt
        logging.info("The current incident state is", curr_incident.state)
        next_message = await handle_serial_message(db=db, incident=curr_incident, message=Body)
    
    if next_message == end_msg:
        await crud.delete_incident(db, curr_incident)
    else:
        logging.info(next_message)
        await send_sms(To, From, next_message)    


async def handle_serial_message(db: AsyncSession, incident: Incident, message: str):
    curr_state = state_to_node[incident.state]
    valid_output, error_msg = None, None

    if message.upper() == skip_msg:
        valid_output = 'N/A'
    elif incident.state == "start":
        valid_output, error_msg = parse_start(message)
    elif incident.state == "facility_name":
        valid_output, error_msg = parse_facility_name(message)
        if valid_output:
            incident.incident_address = loc_to_adr[valid_output]
        
    elif "phone" in incident.state:
        # Standard sequential data extraction
        valid_output, error_msg = parse_phone_number(message)
    elif "address" in incident.state:
        valid_output, error_msg = parse_address(message)
    elif 'incident_was_today' == incident.state:
        if message == 'Y':
            curr_dt = datetime.now()
            valid_output = 'True'
            time = curr_dt.time().replace(second=0, microsecond=0)
            incident.date_of_incident, incident.time_of_incident = curr_dt.date(), time
            curr_state = curr_state.next.next
        elif message == 'n':
            valid_output = 'False'
        else:
            error_msg = "Please respond with either 'Y' for yes or 'n' for no" if message not in ['Y', 'n'] else None
    elif "date" in incident.state:
        valid_output, error_msg = parse_date(message)
    elif "time" in incident.state:
        valid_output, error_msg = parse_time(message)
    elif incident.state == "witness" and message.strip('/').upper() == "NA":
        # Need to skip the next field
        valid_output = "N/A"
        curr_state = curr_state.next
    elif incident.state == "done":
        # TODO Handle the end of message flows gracefully to allow same lifeguard to file multiple reports
        error_msg = "This report has already been concluded."
    else:
        # Handles names
        valid_output = message.capitalize()
    
    if valid_output:
        # Update the database with the validated output
        if incident.state not in ["start", 'incident_was_today']:
            setattr(incident, incident.state, valid_output)
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
    missing_fields = incident_schemas.Incident.model_validate(incident).missing_fields
    logging.info(f"Found the following missing fields from summary: {missing_fields}")
    if not missing_fields:
        incident.state = "ready"
        await db.commit()
        incident_id = incident.pk
        return f"""Your incident report is ready for review. Please confirm your report here:
https://{ROOT_URL}/incident/{incident_id}/review"""

    follow_ups = await generate_incident_followups(model=settings.openai_model, missing_fields=missing_fields)
    logging.info(f"Generated the follow-ups: {follow_ups}")
    follow_ups_dict = follow_ups.model_dump()
    incident.followups = follow_ups_dict
    first_field = missing_fields[0]
    incident.state = first_field
    await db.commit()

    return getattr(follow_ups, first_field)

async def handle_follow_up(db: AsyncSession, incident: Incident, message: str):
    current_field = incident.state
    setattr(incident, current_field, message)

    # Retrieve followups and remove last asked question
    
    incident.followups.pop(current_field, None)
    followups = incident.followups

    # Handle running out of followups
    if not followups:
        incident.state = "ready"
        incident.followups = {}
        incident_id = incident.pk  # Access inside session

        await db.commit()

        return f"""Your incident report is ready for review. Please confirm your report here:
https://{ROOT_URL}/incident/{incident_id}/review"""
    
    # Get the next question and update the incidents current state
    next_field, next_question = next(iter(followups.items()))
    incident.state = next_field
    await db.commit()
    return next_question

def parse_facility_name(message: str) -> tuple[str | None, str | None]:
    facility_scores = [(_name_score(message, facility), facility) for facility in loc_to_adr]
    best = sorted(facility_scores, reverse=True, key=lambda x: x[0])[0]
    if best[0] >= MATCH:
        return best[1], None
    return None, "Please correct the incident name."
    

def parse_phone_number(phone_str: str) -> tuple[str | None, str | None]:
    phone_str = phone_str if phone_str.startswith("+") else "+1" + phone_str
    if phone_str[1:].isdigit() and 11 <= len(phone_str[1:]) < 14:
        return phone_str, None
    return None, "Please input a valid phone number As a single number (ex: (123) 1234-1234 would be 1231234123)."

def parse_date(date_str: str) -> tuple[str | None, str | None]:
    date_list = date_str.split("/")
    if len(date_list) == 3:
        try:
            valid_output, error_msg = datetime.strptime(date_str, "%m/%d/%Y").date(), None
        except ValueError:
            valid_output, error_msg = None, "Please ensure you entered a valid date in the form MM/DD/YYYY"

    return valid_output, error_msg
    
def parse_time(time_str) -> tuple[str | None, str | None]:
    try:
        valid_output, error_msg = datetime.strptime(time_str, '%I:%M%p').time(), None
    except ValueError:
        valid_output, error_msg = None, "Please enter a valid time in the form HH:MMam/pm (ex: 12:30pm)"
    return valid_output, error_msg

def parse_address(addr_str: str) -> tuple[str | None, str | None]:
    logging.info(addr_str)
    location = geolocator.geocode(addr_str, timeout=5)
    if location:
        addr_split = location.address.split(',')
        if len(addr_split) > 5:
            addr_split = addr_split[:2] + [substr  for substr in addr_split if 'County' in substr] + addr_split[-3:-1]
            
        address = ','.join(addr_split)
        return address, None
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


def _name_score(q: str, cand: str) -> float:
    # Normalize once
    qn, cn = _normalize(q), _normalize(cand)
    # Fast fuzzy signals (0..100)
    ts = fuzz.token_set_ratio(qn, cn)
    pr = fuzz.partial_ratio(qn, cn)
    jw = int(jellyfish.jaro_winkler_similarity(qn, cn) * 100)
    # Phonetic bump if close
    qph = " ".join(jellyfish.metaphone(w) for w in qn.split())
    cph = " ".join(jellyfish.metaphone(w) for w in cn.split())
    ph = 12 if fuzz.ratio(qph, cph) >= 90 else 0
    # Lightweight blend → 0..1
    raw = 0.5*ts + 0.35*pr + 0.15*jw + ph
    return max(0.0, min(1.0, raw/112))  # 100 + 12 max ≈ 112

def _normalize(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^\w\s]", " ", s)           # punctuation -> space
    for k,v in ABBREV.items():               # light expansions
        s = re.sub(rf"\b{k}\b", v, s)
    toks = [t for t in s.split() if t not in DROP_TAILS]
    return " ".join(toks)


