from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Optional


class LifeguardPayload(BaseModel):
    name: str = Field(min_length=1)
    phone: str = Field(min_length=12, max_length=14) # 10 DLC with up to 4 for +country code
    region: str

class Lifeguard(LifeguardPayload):
    id: UUID
    created: datetime

    class Config:
        from_attributes = True

class RegionPayload(BaseModel):
    slug: str = Field(min_length=1)
    locations: list[str]
    locations:dict[str, str]
    managers: Optional[list[str]] = [] # list of manager/s

class Region(BaseModel):
    id: UUID
    slug: str = Field(min_length=1)
    managers: Any
    locations: dict[str, str] # Maps a location name to an address
    lifeguards: Any
    created: datetime

    class Config:
        from_attributes = True

class ManagerPayload(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field()
    region_slugs: list[str]

class Manager(BaseModel):
    id: UUID
    name: str
    email: str

    class Config:
        from_attributes = True