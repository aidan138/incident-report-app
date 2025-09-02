from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import portal
from ..schemas import schemas


async def get_lifeguard_by_phone(db: AsyncSession, phone: str) -> Optional[portal.Lifeguard]:
    q = await db.execute(select(portal.Lifeguard).where(portal.Lifeguard.phone == phone))
    return q.scalars().first()

async def create_lifeguard(db: AsyncSession, lifeguard: schemas.Lifeguard) -> portal.Lifeguard:
    new_lg = portal.Lifeguard(**lifeguard.model_dump()) # Directly maps schema to model
    db.add(new_lg)
    await db.commit()
    await db.refresh()
    return new_lg
