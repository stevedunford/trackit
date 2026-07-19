"""
vacancy.py

Vacancy models for TeachWhere.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
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
# Job Source
# ---------------------------------------------------------------------

class JobSource(BaseModel):
    """
    A source of teaching vacancies.

    Examples:

        NSW JobFeed

        I Work For NSW

        Priority Recruitment Support

        Teacher Recruitment

        Sydney Catholic Schools
    """

    __tablename__ = "job_sources"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    organisation: Mapped[str | None] = mapped_column(
        String(100)
    )

    base_url: Mapped[str | None] = mapped_column(
        String(255)
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text
    )

    vacancies: Mapped[list["Vacancy"]] = relationship(
        back_populates="source",
        lazy="selectin",
    )

    def __repr__(self) -> str:

        return f"<JobSource {self.name}>"


# ---------------------------------------------------------------------
# Vacancy
# ---------------------------------------------------------------------

class Vacancy(BaseModel):
    """
    A single advertised teaching vacancy.
    """

    __tablename__ = "vacancies"

    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.id"),
        nullable=False,
        index=True,
    )

    school_name: Mapped[str | None] = mapped_column(
        String(255)
    )

    source_id: Mapped[int] = mapped_column(
        ForeignKey("job_sources.id"),
        nullable=False,
        index=True,
    )

    # -------------------------------------------------------------
    # Source identifiers
    # -------------------------------------------------------------

    external_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    reference_number: Mapped[str | None] = mapped_column(
        String(50)
    )

    # -------------------------------------------------------------
    # Display
    # -------------------------------------------------------------

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str | None] = mapped_column(
        String(100)
    )

    # -------------------------------------------------------------
    # Employment
    # -------------------------------------------------------------

    employment_type: Mapped[EmploymentType] = mapped_column(
        SqlEnum(EmploymentType),
        nullable=False,
    )

    full_time: Mapped[bool] = mapped_column(
        Boolean,
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

    graduate_position: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # -------------------------------------------------------------
    # Salary
    # -------------------------------------------------------------

    salary_from: Mapped[int | None] = mapped_column(
        Integer
    )

    salary_to: Mapped[int | None] = mapped_column(
        Integer
    )

    # -------------------------------------------------------------
    # Incentives
    # -------------------------------------------------------------

    has_relocation_support: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    has_recruitment_bonus: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    recruitment_bonus_amount: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # -------------------------------------------------------------
    # Dates
    # -------------------------------------------------------------

    publish_date: Mapped[date | None] = mapped_column(
        Date
    )

    closing_date: Mapped[date | None] = mapped_column(
        Date
    )

    start_date: Mapped[date | None] = mapped_column(
        Date
    )

    end_date: Mapped[date | None] = mapped_column(
        Date
    )

    # -------------------------------------------------------------
    # Content
    # -------------------------------------------------------------

    description_html: Mapped[str | None] = mapped_column(
        Text
    )

    apply_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # -------------------------------------------------------------
    # Scraper
    # -------------------------------------------------------------

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    last_seen: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # -------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------

    school: Mapped["School"] = relationship(
        back_populates="vacancies",
        lazy="selectin",
    )

    source: Mapped["JobSource"] = relationship(
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
            f"{self.title} "
            f"({self.school.name})>"
        )


# ---------------------------------------------------------------------
# Vacancy Subject
# ---------------------------------------------------------------------

class VacancySubject(BaseModel):
    """
    Subject attached to a vacancy.

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
