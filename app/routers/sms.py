from fastapi import APIRouter, Form
from app.services.twilio import send_sms
from twilio.twiml.messaging_response import MessagingResponse

from app.config import settings
from app.core.prompts import build_prompt_flow

router = APIRouter()
twilio_number = settings.twilio_number
workflow_head, state_to_node = build_prompt_flow()


@router.post('/incident')
async def handle_incident_report(From: str = Form(...),
                                To: str = Form(...)):
    
    await send_sms(
        sender=To,
        reciever=From,
        msg="""Hello you have reached Premier Aquatics Incident Report System.

Reply 'Y' to proceed with the incident report or 'n' to end to cancel"""
    )

