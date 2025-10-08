from sqlalchemy import String, ForeignKey, Integer, Table, Column, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.mutable import MutableDict
from app.models.base import Base
from app.models.incidents import Incident
import uuid


manager_region = Table(
    "manager_region",
    Base.metadata,
    Column("manager_id", UUID(as_uuid=True), ForeignKey("managers.pk")),
    Column("region_id", UUID(as_uuid=True), ForeignKey("regions.pk"))
)


class Manager(Base):
    __tablename__ = 'managers'
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    regions: Mapped[list['Region']] = relationship(
        secondary=manager_region, back_populates='managers', lazy='selectin'
    )

class Region(Base):
    __tablename__ = 'regions'
    slug: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    managers: Mapped[list["Manager"]] = relationship(
        secondary=manager_region, back_populates='regions', lazy='selectin'
    )
    
    locations: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON),
        nullable=False,
        default=dict,
    )
    
    incident_reports: Mapped[list['Incident']] = relationship(
        back_populates='region',
        cascade='all, delete-orphan' # Deletes all incident reports associated with a region if region deletedn
    )

    lifeguards: Mapped[list["Lifeguard"]] = relationship(backref="region")

class Lifeguard(Base):
    __tablename__ = "lifeguards"
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    region_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("regions.pk"))
    
    def __repr__(self) -> str:
        return f"<Lifeguard (id={self.pk}), name: {self.name}, phone number: {self.phone}, region: {self.region}>"