import uuid
from sqlalchemy.orm import Mapped
from datetime import datetime
from sqlalchemy import orm

class Base(orm.DeclarativeBase):
    """Base database model."""

    pk: Mapped[uuid.UUID] = orm.mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    created: Mapped[datetime] = orm.mapped_column(
        default=datetime.now
    )