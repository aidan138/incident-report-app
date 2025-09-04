from sqlalchemy import String, ForeignKey, Integer, orm
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.models.base import Base
import uuid


class Incident(Base):
    __tablename__="incidents"

    state: Mapped[str] = mapped_column(String, nullable=False, default="start")
    creator_phone: Mapped[str] = mapped_column(String, nullable=False)

    involved_name: Mapped[str] = mapped_column(String, nullable=True)
    involved_age: Mapped[str] = mapped_column(String, nullable=True)
    involved_phone: Mapped[str] = mapped_column(String, nullable=True)
    involved_guest_of: Mapped[str] = mapped_column(String, nullable=True)
    involved_address: Mapped[str] = mapped_column(String, nullable=True)
    involved_guardian: Mapped[str] = mapped_column(String, nullable=True)

    date_of_incident: Mapped[str] = mapped_column(String, nullable=True)
    time_of_incident: Mapped[str] = mapped_column(String, nullable=True)
    facility_name: Mapped[str] = mapped_column(String, nullable=True)
    incident_address: Mapped[str] = mapped_column(String, nullable=True)
    
    incident_summary: Mapped[str] = mapped_column(String, nullable=True)
    body_part_afflicted: Mapped[str] = mapped_column(String, nullable=True)

    employee_involved: Mapped[str] = mapped_column(String, nullable=True) # yes or no
    security_contacted: Mapped[str] = mapped_column(String, nullable=True) # yes or no
    law_contacted: Mapped[str] = mapped_column(String, nullable=True) # yes or no
    transported_ambulance: Mapped[str] = mapped_column(String, nullable=True)
    ambulance_to_where: Mapped[str] = mapped_column(String, nullable=True)
    type_of_incident: Mapped[str] = mapped_column(String, nullable=True)
    where_incident_occurred: Mapped[str] = mapped_column(String, nullable=True)
    
    # SAMPLE answers
    signs_symptoms: Mapped[str] = mapped_column(String, nullable=True)
    allergies: Mapped[str] = mapped_column(String, nullable=True)
    medications: Mapped[str] = mapped_column(String, nullable=True)
    past_history: Mapped[str] = mapped_column(String, nullable=True)
    last_food_drink: Mapped[str] = mapped_column(String, nullable=True)
    events_leading_up: Mapped[str] = mapped_column(String, nullable=True)

    type_of_injury: Mapped[str] = mapped_column(String, nullable=True)

    employee_completing_report: Mapped[str] = mapped_column(String, nullable=True)
    date_of_report: Mapped[str] = mapped_column(String, nullable=True)
    witness: Mapped[str] = mapped_column(String, nullable=True)
    witness_phone_number: Mapped[str] = mapped_column(String, nullable=True)

