from sqlalchemy import String, ForeignKey, Integer, orm
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.models.base import Base
import uuid


class Incident(Base):
    __tablename__="incidents"

    state: Mapped[str] = mapped_column(String, nullable=False, default="start")
    creator_phone: Mapped[str] = mapped_column(String, nullable=False)

    involved_name: Mapped[str]
    involved_age: Mapped[str]
    involved_phone: Mapped[str]
    involved_guest_of: Mapped[str]
    involved_address: Mapped[str]
    involved_guardian: Mapped[str]

    date_of_incident: Mapped[str]
    time_of_incident: Mapped[str]
    facility_name: Mapped[str]
    incident_address: Mapped[str]
    
    incident_summary: Mapped[str]
    body_part_afflicted: Mapped[str]

    employee_involved: Mapped[str] # yes or no
    security_contacted: Mapped[str] # yes or no
    law_contacted: Mapped[str] # yes or no
    transported_ambulance: Mapped[str]
    ambulance_to_where: Mapped[str]
    type_of_incident: Mapped[str]
    where_incident_occurred: Mapped[str]
    
    # SAMPLE answers
    signs_symptoms: Mapped[str]
    allergies: Mapped[str]
    medications: Mapped[str]
    past_history: Mapped[str]
    last_food_drink: Mapped[str]
    events_leading_up: Mapped[str]

    type_of_injury: Mapped[str]

    employee_completing_report: Mapped[str]
    date_of_report: Mapped[str]
    witness: Mapped[str]
    witness_phone_number: Mapped[str]

