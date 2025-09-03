from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import portal, incidents
from ..schemas import schemas


async def get_lifeguard_by_phone(db: AsyncSession, phone: str) -> Optional[portal.Lifeguard]:
    q = await db.execute(select(portal.Lifeguard).where(portal.Lifeguard.phone == phone))
    scalars = await q.scalars()
    return await scalars.first()

async def create_lifeguard(db: AsyncSession, lifeguard: schemas.Lifeguard) -> portal.Lifeguard:
    new_lg = portal.Lifeguard(**lifeguard.model_dump()) # Directly maps schema to model
    db.add(new_lg)
    await db.commit()
    await db.refresh(new_lg)
    return new_lg

async def get_incident_by_phone(db: AsyncSession, phone: str) -> Optional[incidents.Incident]:
    q = await db.execute(select(incidents.Incident).where((incidents.Incident.creator_phone == phone) & (incidents.Incident.state != 'done')))
    scalars = await q.scalars()
    return await scalars.first()

async def create_incident(db: AsyncSession, phone: str) -> incidents.Incident:
    new_incident = incidents.Incident(employee_phone=phone)
    db.add(new_incident)
    await db.commit()
    await db.refresh(new_incident)
    return new_incident