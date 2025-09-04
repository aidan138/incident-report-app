from twilio.rest import Client
from app.config import settings

account_sid = settings.twilio_sid
auth_token = settings.twilio_token

client = Client(account_sid, auth_token)

async def send_sms(sender: str, reciever: str, msg: str):
    print(f"Sending message {msg} from {sender} to {reciever}")
    message = client.messages.create(
        from_= sender,
        body=msg,
        to=reciever,
    )
    return {"status": f"{message.status}"}