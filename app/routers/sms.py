from fastapi import APIRouter
from twilio.rest import Client
from app.config import settings

account_sid = settings.twilio_sid
auth_token = settings.twilio_token
twilio_number = settings.twilio_number
test_number = settings.test_number

client = Client(account_sid, auth_token)

router = APIRouter()

@router.post('/send')
async def send_msg(msg: str = 'Hello World!'):
    message = client.messages.create(
        from_= twilio_number,
        body=msg,
        to= test_number,
    )
    return {"status": f"{message.status}"}