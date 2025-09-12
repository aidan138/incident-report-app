from app.schemas import incident_schemas
from app.models import incidents


def test_sample_missing_fields():
    kwargs = {
    "state": "start",
    "creator_phone": "5551112222",
    "employee_completing_report": "John Smith",
    "date_of_report": "2025-09-10",

    "person_involved_name": "Alice Johnson",
    "person_involved_age": "34",
    "person_involved_phone_number": "5553334444",
    "person_involved_guest_of": "Company",
    "person_involved_address": "123 Main St, Los Angeles, CA",
    "person_involved_guardian": "N/A",

    "date_of_incident": "2025-09-01",
    "time_of_incident": "14:30",
    "facility_name": "Main Gym",
    "incident_address": "123 Main St, Los Angeles, CA",

    "incident_summary": "Slip and fall in gymnasium.",
    "witness": "Robert Lee",
    "witness_phone": "5556667777",

    "body_part_afflicted": "Left ankle",
    "type_of_incident": "first_aid",
    "type_of_injury": "bump_bruise",
    "was_employee_involved": "no",
    "was_security_contacted": "yes",
    "was_law_contacted": "no",
    "was_transported_ambulance": "yes",
    "ambulance_to_where": "City Hospital",

    "signs_symptoms": "Swelling, pain",
    "allergies": '',
    "medications": "Ibuprofen",
    "past_history": "No prior ankle injuries",
    "last_food_drink": "Lunch at 12:00",
    "events_leading_up": "Running on gym floor, slipped on wet spot",
}
    incident = incidents.Incident(**kwargs)
    missing_fields = incident_schemas.Incident.model_validate(incident).missing_fields
    assert len(missing_fields) == 1
    assert ["allergies"] == missing_fields
