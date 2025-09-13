from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from sqlalchemy.future import select
from ..models import portal, incidents
from ..schemas import incident_schemas, portal_schemas
from typing import Iterable


async def get_lifeguard_by_phone(db: AsyncSession, phone: str) -> Optional[portal.Lifeguard]:
    q = await db.execute(select(portal.Lifeguard).where(portal.Lifeguard.phone == phone))
    scalars = await q.scalars()
    return await scalars.first()

async def create_lifeguard(db: AsyncSession, lifeguard: portal_schemas.Lifeguard) -> portal.Lifeguard:
    new_lg = portal.Lifeguard(**lifeguard.model_dump()) # Directly maps schema to model
    db.add(new_lg)
    await db.commit()
    await db.refresh(new_lg)
    return new_lg

async def get_incident_by_phone(db: AsyncSession, phone: str) -> Optional[incidents.Incident]:
    q = await db.execute(select(incidents.Incident).where((incidents.Incident.creator_phone == phone) & (incidents.Incident.state != 'done')))
    scalars =  q.scalars()
    return scalars.first()

async def create_incident(db: AsyncSession, phone: str) -> incidents.Incident:
    new_incident = incidents.Incident(creator_phone=phone)
    db.add(new_incident)
    await db.commit()
    await db.refresh(new_incident)
    return new_incident

async def delete_incident(db: AsyncSession, incident: incidents.Incident) -> None:
    await db.delete(incident)
    await db.commit()

async def update_incident_fields(db: AsyncSession, incident_pk: int, fields_to_values: dict[str, str]) -> int:
    """Update multiple incident fields in a grouped update given a incident primary key.

    Args:
        db (AsyncSession): The reference to the database.
        incident_pk (int): The primary key of the incident to be updated.
        fields_to_values (dict[str, str]): dictionary containing keys=field, values=content for incident reports.

    Returns:
        int: The number of rows updated in the database.
    """
    statement = (
        update(incidents.Incident)
        .where(incidents.Incident.pk == incident_pk)
        .values(fields_to_values)
        .execution_options(synchronize_session="fetch")
    )
    result = await db.execute(statement=statement)
    await db.commit()
    return result.rowcount

# async def update_incident(db: AsyncSession, incident: incidents.Incident) -> incidents.Incident:
#     await db.commit()
#     await db.refresh(incident)
