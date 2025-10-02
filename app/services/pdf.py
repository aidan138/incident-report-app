import os
from pypdf import PdfReader, PdfWriter
from app.models.incidents import Incident
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.config import settings
import textwrap
import logging
import asyncio
from fastapi import HTTPException
from app.core.exceptions import is_transient_smtp_error
from io import BytesIO
from starlette.datastructures import UploadFile, Headers


conn = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM=settings.mail_from,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

TEMPLATE_PDF = "./app/templates/Fillable Blank Incident Report (2)[35].pdf"

SUMMARY_LINE_LENGTH = 88
CHECKBOX_MAPPING = {
    "type_of_injury" : {
        'Splinter': 'injury_splinter',
        'Burn' : 'injury_burn',
        'HeatRelatedIllness': 'injury_heat',
        'BumpBruise' : 'injury_bump',
        'DentalInjury' : 'injury_dental',
        'HeadNeckSpinalInjury' : 'injury_head_neck',
        'AnimalBiteSting' : 'injury_animal_bite',
        'Stroke' : 'injury_stroke',
        'Choking' : 'injury_choking',
        'CutScrape' : 'injury_cut',
        'HeartAttack' : 'injury_heart',
        'Other' : 'injury_other',
    },
    "type_of_incident": {
        'FirstAid': 'incident_first_aid',
        'Altercation': 'incident_altercation',
        'Rescue': 'incident_rescue',
        'Other': 'incident_other',
    },
}

MAX_ATTEMPTS = 5
BASE_DELAY = 0.5
MAX_DELAY = 15.0
TIMEOUT = 15

logger = logging.getLogger(__name__)



def generate_pdf_bytes(incident: Incident):
    reader = PdfReader(TEMPLATE_PDF)
    writer = PdfWriter()

    writer.append(reader)
    writer.set_need_appearances_writer(True)

    data = _get_incident_dict(incident)
    writer.update_page_form_field_values(
        page=None,                 # None = all pages (per docs)
        fields=data,
        auto_regenerate=False,     # leave to viewers; we already set NeedAppearances
        flatten=False              # set True if you want to burn the text in (see below)
    )

    buffer = BytesIO()
    writer.write(buffer)
    buffer.seek(0)

    return buffer.getvalue()

def _get_incident_dict(incident: Incident):
    data = incident.to_dict()
    data["date_of_report"] = data["created"].strftime("%m/%d/%Y")
    data["date_of_incident"] = data["date_of_incident"].strftime("%m/%d/%Y")
    data["time_of_incident"] = data["time_of_incident"].strftime("%I:%M%p")
    summary = data["incident_summary"]

    # Iterate through checkboxes
    for enum, mapping in CHECKBOX_MAPPING.items():
        field = data[enum].name
        for value, field_name in mapping.items():

            # Only mark checkbox if it is the one identified
            data[field_name] = '/Yes' if  field == value else '/Off'

    # chunk the summary text to meet line  length
    summary_list = textwrap.wrap(summary, SUMMARY_LINE_LENGTH)
    data["incident_summary"] = '\n'.join(summary_list)
    return data

async def email_pdf_bytes(
        recipient: str,
        subject: str,
        body: str,
        filename: str,
        pdf_bytes: bytes,        
):
    upload = UploadFile(
        filename=filename,
        file=BytesIO(pdf_bytes),
        headers=Headers({"content-type": "application/pdf"}),
    )

    msg = MessageSchema(
        subject=subject,
        recipients=[recipient],
        body=body,
        subtype=MessageType.html,
        attachments=[upload]
    )
    
    fm = FastMail(conn)
    last_exc = None

    for attempt in range(1, MAX_ATTEMPTS+1):
        try:
            await asyncio.wait_for(fm.send_message(msg), TIMEOUT)
            logger.info("Email sent to %s on attempt %d", recipient, attempt)
            return

        except Exception as exc:
            last_exc = exc

            should_retry = is_transient_smtp_error(exc) # Determine if it is smtp 
            code = getattr(exc, "code", None)
            message = getattr(exc, "message", None) or str(exc)
            logger.warning(
                "Email send failed (attempt %d/%d). code=%s transient=%s error=%s",
                attempt, MAX_ATTEMPTS, code, should_retry, message,
                exc_info=True
            )

            delay = min(BASE_DELAY * 2**(attempt-1), MAX_DELAY)
            try:
                asyncio.sleep(delay)
            except asyncio.CancelledError: # Raise outside exception
                break
    
    raise HTTPException(
        status_code=500, detail=f'Failed to send email to recipient {recipient} after {MAX_ATTEMPTS} retries'
    ) from last_exc