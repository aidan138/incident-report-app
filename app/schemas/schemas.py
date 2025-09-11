from uuid import UUID
from pydantic import BaseModel, Field, model_validator, ConfigDict
from datetime import datetime
from typing import Optional, Literal
from enum import Enum

class TypeOfIncident(Enum):
    FirstAid = "first_aid"
    Altercation = "altercation"
    Rescue = "rescue"
    Other = "other"

class TypeofInjury(Enum):
    Splinter = "splinter"
    Burn = "burn"
    HeatRelatedIllness = "heat_related_illness"
    BumpBruise = "bump_bruise"
    DentalInjury = "dental_injury"
    HeadNeckSpinalInjury = "head_neck_spinal_injury"
    AnimalBiteSting = "animal_bite_sting"
    Stroke = "stroke"
    Choking = "choking"
    CutScrape = "cut_scrape"
    HeartAttack = "heart_attack"
    Other = "other"

class LifeguardPayload(BaseModel):
    name: str = Field(min_length=1)
    phone: str = Field(min_length=12, max_length=14) # 10 DLC with up to 4 for +country code
    region: str

class Lifeguard(LifeguardPayload):
    id: UUID
    created: datetime

    class Config:
        from_attributes = True


class Region(BaseModel):
    id: UUID
    name: str = Field(min_length=1)
    created: datetime

    class Config:
        from_attributes = True

class Manager(BaseModel):
    id: UUID
    name: str = Field(min_length=1)

    class Config:
        from_attributes = True

class IncidentSummary(BaseModel):
    body_part_afflicted: Optional[str] = None
    type_of_incident: TypeOfIncident
    type_of_injury: TypeofInjury
    was_employee_involved: Optional[Literal["yes", "no"]] = None
    was_security_contacted: Optional[Literal["yes", "no"]] = None
    was_law_contacted: Optional[Literal["yes", "no"]] = None
    was_transported_ambulance: Optional[Literal["yes", "no"]] = None
    ambulance_to_where: Optional[str] = None
    signs_symptoms: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    past_history: Optional[str] = None
    last_food_drink: Optional[str] = None
    events_leading_up: Optional[str] = None

class Incident(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # instead of class Config


    state: str
    creator_phone: str
    employee_completing_report: str

    person_involved_name: str
    person_involved_age: str
    person_involved_phone_number: str
    person_involved_guest_of: str
    person_involved_address: str
    person_involved_guardian: str

    time_of_incident: str
    facility_name: str
    incident_address: str
    
    date_of_incident: str
    incident_summary: str
    witness: Optional[str] = None
    witness_phone: Optional[str] = None

    # Potentially missing fields
    body_part_afflicted: Optional[str] = None
    type_of_incident: TypeOfIncident
    type_of_injury: TypeofInjury
    was_employee_involved: Optional[Literal["yes", "no"]] = None
    was_security_contacted: Optional[Literal["yes", "no"]] = None
    was_law_contacted: Optional[Literal["yes", "no"]] = None
    was_transported_ambulance: Optional[Literal["yes", "no"]] = None
    ambulance_to_where: Optional[str] = None
    signs_symptoms: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    past_history: Optional[str] = None
    last_food_drink: Optional[str] = None
    events_leading_up: Optional[str] = None

    missing_fields: list[str] = []


    @model_validator(mode="after")
    def get_missing_fields(cls, values):

        missing = []

        # Define groups of fields that must be filled together
        groups = [
            [
                "was_transported_ambulance", # Ambulance check
                "ambulance_to_where",
            ],
            [
                "signs_symptoms", # SAMPLE acronym
                "allergies",
                "medications",
                "past_history",
                "last_food_drink",
                "events_leading_up",
            ],
        ]

        for group in groups:
            filled = any(getattr(values, field, None) for field in group)
            if filled:
                for field in group:
                    if not getattr(values, field, None):
                        missing.append(field)

        values.missing_fields = missing
        return values