"""
school.py

School models for TRACKit.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    Enum as SqlEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import BaseModel


# ---------------------------------------------------------------------
# Type Check Code
# ---------------------------------------------------------------------

if TYPE_CHECKING:
    from .geography import Locality
    from .reference import SchoolType
    from .vacancy import Vacancy


# ---------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------

class AliasSource(Enum):
    JOBFEED = "JobFeed"
    SCHOOL_FINDER = "School Finder"
    MANUAL = "Manual"
    HISTORICAL = "Historical"


class SchoolSector(Enum):
    GOVERNMENT = "Government"
    CATHOLIC = "Catholic"
    INDEPENDENT = "Independent"


class SchoolSource(Enum):
    NSW_DATASET = "NSW Dataset"
    MANUAL = "Manual"
    IMPORTED = "Imported"


class Remoteness(Enum):
    MAJOR_CITIES = "Major Cities of Australia"
    INNER_REGIONAL = "Inner Regional Australia"
    OUTER_REGIONAL = "Outer Regional Australia"
    REMOTE = "Remote Australia"
    VERY_REMOTE = "Very Remote Australia"


# ---------------------------------------------------------------------
# School
# ---------------------------------------------------------------------

class School(BaseModel):
    """
    NSW schools.
    """

    __tablename__ = "schools"

    __table_args__ = (
        UniqueConstraint(
            "school_code",
            name="uq_school_code",
        ),
    )

    locality_id: Mapped[int] = mapped_column(
        ForeignKey("localities.id"),
        nullable=False,
        index=True,
    )

    school_type_id: Mapped[int] = mapped_column(
        ForeignKey("school_types.id"),
        nullable=False,
        index=True,
    )

    school_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    short_name: Mapped[str | None] = mapped_column(
        String(80)
    )

    address: Mapped[str | None] = mapped_column(
        String(200)
    )

    town_suburb: Mapped[str | None] = mapped_column(
        String(100)
    )

    postcode: Mapped[str | None] = mapped_column(
        String(10)
    )

    phone: Mapped[str | None] = mapped_column(
        String(30)
    )

    email: Mapped[str | None] = mapped_column(
        String(150)
    )

    website: Mapped[str | None] = mapped_column(
        String(255)
    )

    remoteness: Mapped[Remoteness] = mapped_column(
        SqlEnum(Remoteness),
        nullable=False,
    )

    sector: Mapped[SchoolSector] = mapped_column(
        SqlEnum(SchoolSector),
        default=SchoolSector.GOVERNMENT,
        nullable=False,
    )

    foei: Mapped[int | None] = mapped_column(
        Integer
    )

    icsea: Mapped[int | None] = mapped_column(
        Integer
    )

    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    enrolment: Mapped[int | None]

    transfer_points: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    connected_communities: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    year_from: Mapped[int | None]

    year_to: Mapped[int | None]

    principal: Mapped[str | None] = mapped_column(
        String(100)
    )

    selective: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    boarding: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    source: Mapped[SchoolSource] = mapped_column(
        SqlEnum(SchoolSource),
        default=SchoolSource.NSW_DATASET,
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    last_updated: Mapped[date | None] = mapped_column(
        Date
    )

    locality: Mapped["Locality"] = relationship(
        back_populates="schools",
        lazy="selectin",
    )

    school_type: Mapped["SchoolType"] = relationship(
        back_populates="schools",
        lazy="selectin",
    )

    vacancies: Mapped[list["Vacancy"]] = relationship(
        back_populates="school",
        lazy="selectin",
    )

    aliases: Mapped[list["SchoolAlias"]] = relationship(
        back_populates="school",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<School {self.school_code} - {self.name}>"


# ---------------------------------------------------------------------
# School Alias
# ---------------------------------------------------------------------

class SchoolAlias(BaseModel):
    """
    Alternative names for a school.

    Used to match historical JobFeeds and other data sources where
    the published school name differs from the canonical name.
    """

    __tablename__ = "school_aliases"

    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    source: Mapped[AliasSource | None] = mapped_column(
        SqlEnum(AliasSource)
    )

    school: Mapped["School"] = relationship(
        back_populates="aliases",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<SchoolAlias {self.name}>"
