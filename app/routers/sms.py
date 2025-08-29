import os
import dotenv
from fastapi import APIRouter
from twilio import Client

dotenv.load_dotenv()
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_number = os.environ['TWILIO_NUMBER']
test_number = os.environ['AIDAN_NUMBER']

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