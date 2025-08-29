import enum
from dataclasses import dataclass
from typing import Optional


class InvolvedPersonState(str, enum.Enum):
    start = 'start'
    involved_name = 'person_involved_name'
    involved_age = 'person_involved_age'
    involved_phone = 'person_involved_phone_number'
    involved_guest_of = 'person_involved_guest_of'
    involved_address = 'person_involved_address'
    involved_guardian = 'person_involved_guardian'

class BasicIncidentInfoState(str, enum.Enum):
    # Incident info
    doi = 'date_of_incident'
    toi = 'time_of_incident'
    facility_name = 'facility_name'
    incident_address = 'address_of_incident'
    # employee = 'employee_involved'
    # security_contacted = 'security_contacted'
    # contacted_911 = '911_called'
    # transported_by_ambulance = 'transported_by_ambulance'
    # where = 'if_transported_by_ambulance_where'

PROMPTS = {
    'start': """Hello you have reached Premier Aquatics Incident Report System.

Reply 'Y' to proceed with the incident report or 'n' to end to cancel""",
    'person_involved_name': "What is the name of the person involved in the injury/incident?",
    'person_involved_age': "What is the age of the person involved in the incident?",
    'person_involved_phone_number': "As a single number (ex: (123) 1234-1234 would be 1231234123), describe the phone number of the person involved in the incident.",
    'person_involved_guest_of': "Who is the person involved in the incident a guest of?",
    'person_involved_address': "In the form (street address, city name, state, zipcode), what is the current addres the person involved lives at?",
    'person_involved_guardian': "What is the name of the legal guardian  of the person involved?",
    'date_of_incident': "In MM/DD/YY format, what was the date the incident occurred at?",
    }



@dataclass
class StateNode:
    field_name: str
    prompt: str
    next: Optional["StateNode"] = None


def build_prompt_flow() -> tuple[StateNode, list[StateNode]]:
    mandatory_states = list(InvolvedPersonState) + list(BasicIncidentInfoState)
    head = None
    prev_node = None
    field_to_node: dict[str, StateNode] = {}

    for state in mandatory_states:
        node = StateNode(field_name=state, prompt=PROMPTS[state])
        field_to_node[state] = node
        
        if prev_node:
            prev_node.next = node
        else:
            head = node
        
        prev_node = node
    
    return head, field_to_node
