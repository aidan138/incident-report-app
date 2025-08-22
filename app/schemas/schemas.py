from uuid import UUID
from pydantic import BaseModel, NaiveDatetime
from datetime import datetime


class LifeguardCreate(BaseModel):
    name: str
    phone: str
    region: str

class Lifeguard(LifeguardCreate):
    id: UUID
    created: datetime

    class Config:
        orm_mode = True


class Region(BaseModel):
    id: UUID
    name: str
    created: NaiveDatetime

    class Config:
        orm_mode = True

class Manager(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True
    