"""
vacancy.py

Vacancy models for TRACKit.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import BaseModel


if TYPE_CHECKING:
    from .reference import Subject
    from .school import School


# ---------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------

class EmploymentType(Enum):
    """Type of employment."""

    PERMANENT = "Permanent"
    TEMPORARY = "Temporary"


class RequirementType(Enum):
    """Teaching requirement."""

    APPROVED = "Approved"
    WILLING = "Willing"


# ---------------------------------------------------------------------
# JobFeed
# ---------------------------------------------------------------------

class JobFeed(BaseModel):
    """
    One weekly JobFeed publication.
    """

    __tablename__ = "jobfeed_issues"

    issue_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        unique=True,
        index=True,
    )

    pdf_filename: Mapped[str | None] = mapped_column(
        String(255)
    )

    vacancies: Mapped[list["Vacancy"]] = relationship(
        back_populates="jobfeed",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<JobFeed {self.issue_date}>"


class Vacancy(BaseModel):
    """
    A single advertised vacancy.
    """

    __tablename__ = "vacancies"

    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.id"),
        nullable=False,
        index=True,
    )

    jobfeed_id: Mapped[int] = mapped_column(
        ForeignKey("jobfeed_issues.id"),
        nullable=False,
        index=True,
    )

    advert_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    employment_type: Mapped[EmploymentType] = mapped_column(
        SqlEnum(EmploymentType),
        nullable=False,
    )

    full_time: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    position_fraction: Mapped[float] = mapped_column(
        default=1.0,
        nullable=False,
    )

    number_of_positions: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date
    )

    end_date: Mapped[date | None] = mapped_column(
        Date
    )

    closing_date: Mapped[date | None] = mapped_column(
        Date
    )

    advert_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    school: Mapped["School"] = relationship(
        back_populates="vacancies",
        lazy="selectin",
    )

    jobfeed: Mapped["JobFeed"] = relationship(
        back_populates="vacancies",
        lazy="selectin",
    )

    subjects: Mapped[list["VacancySubject"]] = relationship(
        back_populates="vacancy",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Vacancy "
            f"{self.school.name} "
            f"{self.employment_type.value}>"
        )


# ---------------------------------------------------------------------
# Vacancy Subject
# ---------------------------------------------------------------------

class VacancySubject(BaseModel):
    """
    Subject attached to a vacancy.

    A vacancy may have multiple subjects.

    Example:

        Approved -> Industrial Technology (Metal)

        Willing -> Technology Mandatory
    """

    __tablename__ = "vacancy_subjects"

    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id"),
        nullable=False,
        index=True,
    )

    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id"),
        nullable=False,
        index=True,
    )

    requirement: Mapped[RequirementType] = mapped_column(
        SqlEnum(RequirementType),
        nullable=False,
    )

    vacancy: Mapped["Vacancy"] = relationship(
        back_populates="subjects",
        lazy="selectin",
    )

    subject: Mapped["Subject"] = relationship(
        back_populates="vacancy_subjects",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<VacancySubject "
            f"{self.subject.code} "
            f"{self.requirement.value}>"
        )
