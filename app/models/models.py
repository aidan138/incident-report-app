import uuid
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from datetime import datetime
from ..db import Base


def generate_uuid():
    return str(uuid.uuid4())

class Lifeguard(Base):
    __tablename__ = "lifeguards"
    id = Column(Integer, primary_key=True, index=True, default=generate_uuid)
    name = Column(String)
    phone = Column(String, unique=True, index=True, nullable=False)
    region = relationship("Region")
    created = Column(DateTime, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Lifeguard (id={self.id}), name: {self.name}, phone number: {self.phone}, region: {self.region}>"
    # TODO add 1 : many Incident reports 

class Region(Base):
    __tablename__ = 'regions'

    id = Column(String, primary_key=True, default=generate_uuid)
    created = Column(DateTime, nullable=False)
    
    manager_id = Column(Integer, ForeignKey("managers.id"))

class Manager(Base):
    __tablename__ = 'managers'
    id = Column(Integer, primary_key=True, index=True, default=generate_uuid)
    name = Column(String)

