"""
reference.py

Reference / lookup models used throughout TRACKit.
These tables contain relatively static data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import BaseModel

if TYPE_CHECKING:
    from .school import School
    from .vacancy import VacancySubject


class SchoolType(BaseModel):
    """
    NSW Department school type.

    Examples:
        High School
        Central School
        Community School
        Public School
        SSP
    """

    __tablename__ = "school_types"

    code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        unique=True,
        index=True,
    )

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

    schools: Mapped[list["School"]] = relationship(
        back_populates="school_type",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<SchoolType {self.name}>"


class Faculty(BaseModel):
    """
    School faculty.

    Examples:
        TAS
        CAPA
        Science
        Mathematics
        English
    """

    __tablename__ = "faculties"

    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    sort_order: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    subjects: Mapped[list["Subject"]] = relationship(
        back_populates="faculty",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Faculty {self.code}>"


class Subject(BaseModel):
    """
    NSW teaching subject.

    Examples:

        ITX
        Technology Mandatory

        IPT
        Information Processes & Technology

        SDD
        Software Design & Development
    """

    __tablename__ = "subjects"

    faculty_id: Mapped[int] = mapped_column(
        ForeignKey("faculties.id"),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    sort_order: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    faculty: Mapped["Faculty"] = relationship(
        back_populates="subjects",
        lazy="selectin",
    )

    active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    vacancy_subjects: Mapped[list["VacancySubject"]] = relationship(
        back_populates="subject",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Subject {self.code}>"
