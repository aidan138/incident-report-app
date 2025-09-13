import pytest
from app.services.gpt import extract_incident_info, generate_incident_followups
from app.schemas.incident_schemas import IncidentSummary
import logging

logging.basicConfig(level=logging.INFO, force=True)

@pytest.mark.asyncio
async def test_basic_incident_extraction():
    summary = """At approximately 1:10pm on Tuesday July 1st, 2025 Roman Velasquez age 8 years old was playing in the splash pad when he felt his nose starting to bleed and approached Marilyn Bottelo guarding Lifeguard Station three that he was bleeding. Botello guided Velasquez outside the water and signaled Lifeguard manager Ricardo Octaviaro. Octaviaro controlled the bleeding by having Velasquez Pinch the bridge of his nose, lean forward, as Octaviaro had the gauze underneath the nostril, not inside so the blood would be caught by the gauze. Velasquez nose stopped bleeding and did not need any further care."""
    response = await extract_incident_info('gpt-5-nano', summary)
    logging.info(f"The ChatGPT summary response is: {response}")
    assert isinstance(response, IncidentSummary)

@pytest.mark.asyncio
async def test_basic_follow_ups():
    missing_fields = ['allergies', 'medications', 'past_history', 'last_food_drink', 'events_leading_up']
    follow_ups = await generate_incident_followups(model='gpt-5-nano', missing_fields=missing_fields)
    logging.info(f"The ChatGPT follow-up questions are: {follow_ups}")
    for missing_field in missing_fields:
        assert hasattr(follow_ups, missing_field)
        assert isinstance(getattr(follow_ups, missing_field), str)
