from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from sqlalchemy.future import select
from ..models import portal, incidents
from ..schemas import portal_schemas
from fastapi import HTTPException


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

async def create_manager(db: AsyncSession, mg: portal_schemas.ManagerPayload):
    print("Adding manager...")
    regions = (
        await db.execute(
            select(portal.Region).where(portal.Region.slug.in_(mg.region_slugs))
        )
    ).scalars().all()
    
    missing = set(mg.region_slugs) - {region.slug for region in regions}
    if missing:
        raise HTTPException(status_code=404, detail=f'Unknown regions: {missing}')
    
    new_manager = portal.Manager(name=mg.name, email=mg.email)
    for rg in regions:
        new_manager.regions.append(rg)

    db.add(new_manager)
    await db.commit()
    await db.refresh(new_manager)
    return new_manager

async def create_region(db: AsyncSession, rg: portal_schemas.RegionPayload):
    if rg.managers:
        managers = (
            await db.execute(
                select(portal.Region).where(portal.Region.managers.name.in_(rg.managers))
            )
        )

        missing = set(rg.managers) - {manager.name for manager in  managers}
    else:
        missing = None

    if missing:
        raise HTTPException(status_code=404, detail=f'Unknown managers: {missing}')
    
    new_region = portal.Region(slug=rg.slug)
    new_region.locations = new_region.locations if new_region.locations else {}
    new_region.locations.update(rg.locations)
    for mgr in rg.managers:
        new_region.managers.append(mgr)
    
    db.add(new_region)
    await db.commit()
    await db.refresh(new_region)
    return new_region


async def get_manager_by_email(db: AsyncSession, email: str):
    q = await db.execute(select(portal.Manager).where(portal.Manager.email == email))
    scalars = q.scalars()
    return scalars.first()

async def get_region_by_slug(db: AsyncSession, slug: str):
    q = await db.execute(select(portal.Region).where(portal.Region.slug == slug))
    scalars = q.scalars()
    return scalars.first()

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

