"""
geography.py

Geographic models for TRACKit.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import BaseModel

if TYPE_CHECKING:
    from .school import School


class Region(BaseModel):
    """
    Geographic region.

    Examples:

        Central West
        Riverina
        Far West
        New England
    """

    __tablename__ = "regions"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(255)
    )

    sort_order: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    localities: Mapped[list["Locality"]] = relationship(
        back_populates="region",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Region {self.name}>"


class Locality(BaseModel):
    """
    Town or locality.

    A locality may contain one or more schools.
    """

    __tablename__ = "localities"

    __table_args__ = (
        UniqueConstraint(
            "name",
            "postcode",
            name="uq_locality_name_postcode",
        ),
    )

    region_id: Mapped[int] = mapped_column(
        ForeignKey("regions.id"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    postcode: Mapped[str | None] = mapped_column(
        String(10)
    )

    lga: Mapped[str | None] = mapped_column(
        String(100)
    )

    population: Mapped[int | None]

    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    region: Mapped["Region"] = relationship(
        back_populates="localities",
        lazy="selectin",
    )

    schools: Mapped[list["School"]] = relationship(
        back_populates="locality",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Locality {self.name}>"
