from fastapi import FastAPI, Request
from twilio.base.exceptions import TwilioRestException
from fastapi.responses import JSONResponse
import requests

def register_exceptions(app: FastAPI):

    @app.exception_handler(TwilioRestException)
    async def twilio_exception_handler(request: Request, exc: TwilioRestException):
        return JSONResponse(
            status_code=400,
            content={"detail": f"Twilio error: {exc.msg}"}
        )
    
    @app.exception_handler(requests.exceptions.Timeout)
    async def timeout_exception_handler(request: Request, exc: requests.exceptions.Timeout):
        return JSONResponse(
            status_code=504,
            content={"detail": f"Outgoing request timed out"}
        )