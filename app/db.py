from collections.abc import AsyncGenerator
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

raw =settings.database_url
if raw.startswith("postgresql://"):
    raw = raw.replace("postgresql://", "postgresql+asyncpg://", 1)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(raw, echo=True) # Creates a database engine TODO Remove echo in production
    factory = async_sessionmaker(engine)
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except exc.SQLAlchemyError as error:
            await session.rollback()
            raise
