import pytest
from app.services.gpt import extract_incident_json
from app.config import settings
from app.schemas.schemas import IncidentSummary


@pytest.mark.asyncio
async def test_basic_incident_extraction():
    summary = """At approximately 1:10pm on Tuesday July 1st, 2025 Roman Velasquez age 8 years old was playing in the splash pad when he felt his nose starting to bleed and approached Marilyn Bottelo guarding Lifeguard Station three that he was bleeding. Botello guided Velasquez outside the water and signaled Lifeguard manager Ricardo Octaviaro. Octaviaro controlled the bleeding by having Velasquez Pinch the bridge of his nose, lean forward, as Octaviaro had the gauze underneath the nostril, not inside so the blood would be caught by the gauze. Velasquez nose stopped bleeding and did not need any further care"""
    response = await extract_incident_json('gpt-5-nano', summary)
    print(response)
    assert isinstance(response, IncidentSummary)
