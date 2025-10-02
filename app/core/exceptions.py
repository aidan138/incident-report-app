from fastapi import FastAPI, Request
from twilio.base.exceptions import TwilioRestException
from fastapi.responses import JSONResponse
import requests
from typing import Iterable
from aiosmtplib.errors import (
        SMTPException,
        SMTPConnectError,
        SMTPServerDisconnected,
        SMTPHeloError,
        SMTPAuthenticationError,
        SMTPRecipientsRefused,
        SMTPDataError,
        SMTPTimeoutError,
    )


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

def is_transient_smtp_error(exc: Exception) -> bool:
    """
    Decide if an SMTP-ish exception is worth retrying.

    Rules of thumb:
    - Network/connection/timeouts/disconnects: retry
    - 4xx SMTP codes: retry (temporary)
    - 5xx SMTP codes: don't retry (permanent)
    - Auth errors / bad recipients: don't retry
    """
    transient_buckets: Iterable[type] = (
        SMTPConnectError,
        SMTPServerDisconnected,
        SMTPTimeoutError,
        ConnectionError,
        TimeoutError,
        OSError,  # e.g., DNS hiccups, socket issues
    )
    if isinstance(exc, transient_buckets):
        return True

    # SMTP Response codes if available (aiosmtplib exceptions often carry .code)
    code = getattr(exc, "code", None)
    if isinstance(code, int):
        if 400 <= code < 500:
            return True   # 4xx = temporary
        if code >= 500:
            return False  # 5xx = permanent

    # Specific permanents
    if isinstance(exc, (SMTPAuthenticationError, SMTPRecipientsRefused, SMTPHeloError, SMTPDataError)):
        return False

    # Default: be conservative and do not retry unknown SMTPExceptions with clear non-transient signals
    # but allow generic SMTPException without code once or twice.
    return isinstance(exc, SMTPException)
