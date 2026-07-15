"""
school.py

School models for TRACKit.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
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


class School(BaseModel):
    """
    NSW Government school.
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

    school_code: Mapped[str] = mapped_column(
        String(20),
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

    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    enrolment: Mapped[int | None]

    years_from: Mapped[int | None]

    years_to: Mapped[int | None]

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

    locality: Mapped["Locality"] = relationship(
        back_populates="schools",
        lazy="selectin",
    )

    school_type: Mapped["SchoolType"] = relationship(
        back_populates="schools",
        lazy="selectin",
    )

    incentives: Mapped[list["SchoolIncentive"]] = relationship(
        back_populates="school",
        lazy="selectin",
        cascade="all, delete-orphan",
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


class SchoolAlias(BaseModel):
    """
    Alternative name for a school.

    Used to match historical JobFeeds and other data sources where
    a school's published name differs from its canonical name.

    Examples:
        Dubbo College Senior Campus
        Dubbo College (Senior Campus)
        Dubbo College - Senior Campus
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


class SchoolIncentive(BaseModel):
    """
    Historical incentive record for a school.

    A school may have multiple incentive records over time.
    """

    __tablename__ = "school_incentives"

    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.id"),
        nullable=False,
        index=True,
    )

    points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    recruitment_bonus: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    retention_bonus: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    effective_from: Mapped[int | None]

    effective_to: Mapped[int | None]

    school: Mapped["School"] = relationship(
        back_populates="incentives",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<SchoolIncentive "
            f"{self.points} points "
            f"({self.school.name})>"
        )
