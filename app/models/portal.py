from sqlalchemy import String, ForeignKey, Integer, orm
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.models.base import Base
import uuid


# manager_region = Table(
#     "manager_region",
#     mapped_column("manager_id", ForeignKey("managers.pk"), primary_key=True),
#     mapped_column("region_id", ForeignKey("regions.pk"), primary_key=True)
# )
class ManagerRegion(Base):
    __tablename__ = 'manager_region'

    manager_id: Mapped[int] = mapped_column("manager_id", ForeignKey("managers.pk"), primary_key=True)
    name: Mapped[str] = mapped_column("region_id", ForeignKey('regions.pk'), primary_key=True)


class Region(Base):
    __tablename__ = 'regions'
    manager_id: Mapped[int] = mapped_column(Integer, ForeignKey("managers.pk"))

    managers: Mapped[list["Manager"]] = relationship(
        "Manager",
        secondary=ManagerRegion,
        back_populates="regions"
    )
    
    lifeguards: Mapped[list["Lifeguard"]] = relationship(back_populates="regions")

class Manager(Base):
    __tablename__ = 'managers'
    name: Mapped[str] = mapped_column(String, nullable=False)

    regions: Mapped[list["Region"]] = relationship(
        "region",
        secondary=ManagerRegion,
        back_populates="managers"
    )

class Lifeguard(Base):
    __tablename__ = "lifeguards"
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    region_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("regions.pk"))
    region: Mapped["Region"] = relationship(back_populates="lifeguards")
    
    def __repr__(self) -> str:
        return f"<Lifeguard (id={self.pk}), name: {self.name}, phone number: {self.phone}, region: {self.region}>"