from uuid import UUID
from pydantic import BaseModel, Field
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
    HeartAttack = "HeartAttack"
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
