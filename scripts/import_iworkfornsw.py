"""
import_iworkfornsw.py

Import NSW Department of Education vacancies from an exported
I Work For NSW JSON file.

Usage:

    py scripts/import_iworkfornsw.py jobs.json

"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime, date

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app
from app.extensions import db
from app.models.school import School
from app.models.vacancy import EmploymentType, Vacancy, JobSource
from app.models.school import School


filename = (
    ROOT
    / "imports"
    / "iworkfornsw.json"
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def find_school_name(title: str, schools: list[School],) -> School | None:
    """
    Find the school mentioned in a vacancy title.

    Returns the matching School object,
    or None if no match is found.
    """

    # Longest names first so
    # "Moree Secondary College Albert Street Campus"
    # matches before
    # "Moree Secondary College"

    title_lower = title.lower()

    for school in schools:

        if school.name.lower() in title_lower:
            return school

    return None


def parse_date(value: str | None) -> date | None:
    """
    Convert an ISO-8601 date string into a Python date.
    """

    if not value:
        return None

    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    ).date()


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

app = create_app()

with app.app_context():

    if not filename.exists():

        print()

        print("ERROR")
        print(f"Cannot find:")
        print(f"    {filename}")

        sys.exit(1)

    print(f"Loading {filename}")

    schools = School.query.all()
    schools.sort(
        key=lambda school: len(school.name),
        reverse=True,
    )

    with open(filename, encoding="utf-8") as f:
        data = json.load(f)

    jobs = data["Jobs"]["$values"]

    source = JobSource.query.filter_by(
        name="I Work For NSW"
    ).first()

    if source is None:

        source = JobSource(
            name="I Work For NSW",
            organisation="NSW Department of Education",
            base_url="https://iworkfor.nsw.gov.au"
        )

        db.session.add(source)
        db.session.commit()

    inserted = 0
    updated = 0
    unmatched = 0

    for item in jobs:

        job = item["Job"]

        school = find_school_name(
            job["Title"],
            schools
        )

        if school is None:

            unmatched += 1

            print(f"School not found: {job["Title"]}")

            continue

        vacancy = Vacancy.query.filter_by(
            source_id=source.id,
            external_id=str(job["ID"])
        ).first()

        if vacancy is None:

            vacancy = Vacancy()

            inserted += 1

            db.session.add(vacancy)

        else:

            updated += 1

        vacancy.school = school
        vacancy.school_name = school.name

        vacancy.source = source
        vacancy.external_id = str(job["ID"])

        vacancy.title = job["Title"]

        vacancy.role = (
            job["RoleType"]["$values"][0]["Name"]
            if job["RoleType"]["$values"]
            else None
        )

        if "Temporary" in vacancy.title:
            vacancy.employment_type = EmploymentType.TEMPORARY
        else:
            vacancy.employment_type = EmploymentType.PERMANENT

        vacancy.full_time = True  # TODO: find a flag for it in source data

        vacancy.position_fraction = 1.0  # TODO: also not guaranteed yet

        vacancy.number_of_positions = 1

        vacancy.reference_number = job["ReferenceNumber"]

        vacancy.description_html = job["HTMLDescription"]

        vacancy.apply_url = job["ApplyLink"]

        vacancy.publish_date = parse_date(job["DateFrom"])

        vacancy.closing_date = parse_date(job["DateTo"])

        vacancy.salary_from = job["SalaryFrom"]

        vacancy.salary_to = job["SalaryTo"]

        vacancy.start_date = None

        vacancy.end_date = None

        vacancy.graduate_position = job["IsGraduate"]

    db.session.commit()

    print()
    print("---------------------------------------")
    print(f"Jobs processed : {len(jobs)}")
    print(f"Inserted       : {inserted}")
    print(f"Updated        : {updated}")
    print(f"Unmatched      : {unmatched}")
    print("---------------------------------------")