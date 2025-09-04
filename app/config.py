import logging

from pydantic_settings import BaseSettings
from pydantic import Field
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder of current script
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
logging.basicConfig(level=logging.INFO)

class Settings(BaseSettings):
    project_name: str = "Premier Aquatics Incident Report System"

    database_url: str = ""
    database_url_sync: str = ""
    twilio_sid: str = Field(validation_alias='twilio_account_sid')
    twilio_token: str = Field(validation_alias='TWILIO_AUTH_TOKEN')
    openai_key: str = ""
    twilio_number: str = ""
    test_number: str = ""

    class Config:
        env_file = ENV_PATH
        

settings = Settings()
