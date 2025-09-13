import os
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from app.models.incidents import Incident
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.config import settings
import textwrap

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
OUTPUT_DIR = "./app/tmp"

SUMMARY_LINE_LENGTH = 125
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


def generate_pdf(incident: Incident) -> str:
    """Generate a incident report pdf and return its local filepath"""
    output_path = os.path.join(OUTPUT_DIR, f"incident_{incident.pk}.pdf")
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

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path

def _get_incident_dict(incident: Incident):
    data = incident.to_dict()
    data["date_of_report"] = data["created"].strftime("%m/%d/%Y")
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

async def email_pdf(
        recipient: str,
        subject: str,
        body: str,
        pdf_path: str
):
    
    msg = MessageSchema(
        subject=subject,
        recipients=[recipient],
        body=body,
        subtype=MessageType.html,
        attachments=[pdf_path]
    )
    
    fm = FastMail(conn)
    await fm.send_message(msg)