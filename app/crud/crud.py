from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import models
from ..schemas import schemas


async def get_lifeguard_by_phone(db: AsyncSession, phone: str) -> Optional[models.Lifeguard]:
    q = await db.execute(select(models.Lifeguard).where(models.Lifeguard.phone == phone))
    return q.scalars().first()

async def create_lifeguard(db: AsyncSession, lifeguard: schemas.Lifeguard) -> models.Lifeguard:
    new_lg = models.Lifeguard(**lifeguard.model_dump()) # Directly maps schema to model
    db.add(new_lg)
    await db.commit()
    await db.refresh()
    return new_lg
