from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import models
from schemas import schemas


async def get_life_guard_by_phone(db: AsyncSession, phone: str) -> Optional[models.Lifeguard]:
    q = await db.execute(select(models.Lifeguard).where(models.Lifeguard.phone == phone))
    return q.scalars().first()

async def create_lifeguard(db: AsyncSession, lifeguard: schemas.Lifeguard) -> models.Lifeguard:
    db_l = models.Lifeguard(phone=lifeguard.phone, name=lifeguard.name)
    db.add(db_l)
    await db.commit()
    await db.refresh()
    return db_l
