from sqlalchemy import String, Enum, JSON, Time, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.mutable import MutableDict
from app.models.base import Base
from app.models.portal import Region
from app.schemas.incident_schemas import TypeOfIncident, TypeofInjury
from datetime import date, time
import uuid



class Incident(Base):
    __tablename__="incidents"

    state: Mapped[str] = mapped_column(String, nullable=False, default="start")
    creator_phone: Mapped[str] = mapped_column(String, nullable=False)
    employee_completing_report: Mapped[str] = mapped_column(String, nullable=True)
    region_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("regions.pk"))
    region: Mapped[Region] = relationship(back_populates="incident_reports")

    person_involved_name: Mapped[str] = mapped_column(String, nullable=True)
    person_involved_age: Mapped[str] = mapped_column(String, nullable=True)
    person_involved_phone_number: Mapped[str] = mapped_column(String, nullable=True)
    person_involved_guest_of: Mapped[str] = mapped_column(String, nullable=True)
    person_involved_address: Mapped[str] = mapped_column(String, nullable=True)
    person_involved_guardian: Mapped[str] = mapped_column(String, nullable=True)

    date_of_incident: Mapped[date] = mapped_column(Date, nullable=True)
    time_of_incident: Mapped[time] = mapped_column(Time, nullable=True)
    facility_name: Mapped[str] = mapped_column(String, nullable=True)
    incident_address: Mapped[str] = mapped_column(String, nullable=True)
    
    incident_summary: Mapped[str] = mapped_column(String, nullable=True)
    body_part_afflicted: Mapped[str] = mapped_column(String, nullable=True)

    was_employee_involved: Mapped[str] = mapped_column(String, nullable=True) # yes or no
    was_security_contacted: Mapped[str] = mapped_column(String, nullable=True) # yes or no
    was_911_contacted: Mapped[str] = mapped_column(String, nullable=True) # yes or no
    was_transported_ambulance: Mapped[str] = mapped_column(String, nullable=True)
    ambulance_to_where: Mapped[str] = mapped_column(String, nullable=True)
    type_of_incident: Mapped[TypeOfIncident] = mapped_column(Enum(TypeOfIncident, name="type_of_incident_enum", native_enum=False), nullable=True)
    incident_other_exp: Mapped[str] = mapped_column(String, nullable=True)

    location_of_incident: Mapped[str] = mapped_column(String, nullable=True)
    
    # SAMPLE answers
    signs_symptoms: Mapped[str] = mapped_column(String, nullable=True)
    allergies: Mapped[str] = mapped_column(String, nullable=True)
    medications: Mapped[str] = mapped_column(String, nullable=True)
    past_history: Mapped[str] = mapped_column(String, nullable=True)
    last_food_drink: Mapped[str] = mapped_column(String, nullable=True)
    events_leading_up: Mapped[str] = mapped_column(String, nullable=True)

    type_of_injury: Mapped[TypeofInjury] = mapped_column(
        Enum(TypeofInjury, name="type_of_injury_enum", native_enum=False), nullable=True
    )
    injury_other_exp: Mapped[str] = mapped_column(String, nullable=True)

    witness: Mapped[str] = mapped_column(String, nullable=True)
    witness_phone: Mapped[str] = mapped_column(String, nullable=True)

    followups: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON),
        nullable=False,
        default=dict,
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}