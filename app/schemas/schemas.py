from uuid import UUID
from pydantic import BaseModel, NaiveDatetime, Field
from datetime import datetime


class LifeguardPayload(BaseModel):
    name: str = Field(min_length=1)
    phone: str = Field(min_length=12, max_length=14) # 10 DLC with up to 4 for +country code
    region: str

class Lifeguard(LifeguardPayload):
    id: UUID
    created: datetime

    class Config:
        orm_mode = True


class Region(BaseModel):
    id: UUID
    name: str = Field(min_length=1)
    created: datetime

    class Config:
        orm_mode = True

class Manager(BaseModel):
    id: UUID
    name: str = Field(min_length=1)

    class Config:
        orm_mode = True
    