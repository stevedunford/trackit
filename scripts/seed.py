"""
seed.py

Populate the TRACKit database from the CSV seed files.

This script is intentionally idempotent.

Running it multiple times should not create duplicate records.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from flask import Flask

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.extensions import db

from sqlalchemy import func, select

from app.models.geography import Locality, Region
from app.models.reference import Faculty, SchoolType, Subject


# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

SEED_DIR = PROJECT_ROOT / "seed"


# ---------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------

def print_header() -> None:
    """Display program banner."""

    print("=" * 60)
    print("TRACKit Database Seeder")
    print("=" * 60)
    print(f"Seed directory : {SEED_DIR}")
    print()


def print_footer() -> None:
    """Display completion message."""

    print()
    print("=" * 60)
    print("Seeding complete.")
    print("=" * 60)


def print_summary(
    table: str,
    added: int,
    updated: int,
    unchanged: int,
    errors: int,
) -> None:
    """Print a standard import summary."""

    print(table)

    print(f"  Added      : {added}")
    print(f"  Updated    : {updated}")
    print(f"  Unchanged  : {unchanged}")
    print(f"  Errors     : {errors}")
    print()


def read_csv(filename: Path) -> list[dict[str, str]]:
    """
    Read a UTF-8 CSV file into a list of dictionaries.
    """

    if not filename.exists():
        raise FileNotFoundError(filename)

    with filename.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        return [
            {
                key.strip(): value.strip()
                for key, value in row.items()
            }
            for row in csv.DictReader(file)
        ]


def to_int(value: str | None) -> int | None:
    """Convert CSV value to int."""

    if value is None or value == "":
        return None

    return int(value)


def to_float(value: str | None) -> float | None:
    """Convert CSV value to float."""

    if value is None or value == "":
        return None

    return float(value)


def to_bool(value: str | None) -> bool:
    """Convert CSV value to bool."""

    if value is None:
        return False

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
    }


def print_subject_summary() -> None:
    """
    Print the number of subjects loaded by faculty.
    """

    print("\nSubject totals by faculty")

    rows = (
        db.session.query(
            Faculty.code,
            func.count(Subject.id),
        )
        .join(Subject)
        .group_by(Faculty.code)
        .order_by(Faculty.sort_order)
        .all()
    )

    total = 0

    for faculty_code, count in rows:
        print(f"  {faculty_code:<6} {count:>3}")
        total += count

    print("  ------")
    print(f"  Total  {total}")
    print()


# ---------------------------------------------------------------------
# Loader Functions
# ---------------------------------------------------------------------

def load_regions() -> None:
    """
    Load regions from seed/regions.csv.
    Insert them into the database if they don't already exist.
    Update them if they do exist and have changed.
    """

    print("Loading Regions...")

    filename = SEED_DIR / "regions.csv"

    rows = read_csv(filename)

    added = 0
    updated = 0
    unchanged = 0
    errors = 0

    for line_number, row in enumerate(rows, start=2):

        try:

            name = row.get("name", "").strip()

            if not name:
                raise ValueError("Missing region name")

            region = db.session.execute(
                select(Region).filter_by(name=name)
            ).scalar_one_or_none()

            if region is None:

                region = Region(
                    name=name,
                )

                db.session.add(region)
                added += 1

            else:

                changed = False

                #
                # Future region fields go here.
                #

                if changed:
                    updated += 1
                else:
                    unchanged += 1

        except Exception as ex:

            print(f"  ERROR: {filename.name} line {line_number}: {ex}")
            errors += 1

    try:
        db.session.commit()
    except Exception as ex:
        db.session.rollback()
        print(f"\nDatabase commit failed: {ex}")
        return

    print_summary(
        "Regions",
        added,
        updated,
        unchanged,
        errors,
    )


def load_localities() -> None:
    """
    Load localities from seed/localities.csv.
    Insert them into the database if they don't already exist.
    Update them if they do exist and have changed.
    columns are: name,postcode,region,latitude,longitude,lga
    """

    print("Loading Localities...")

    filename = SEED_DIR / "localities.csv"

    rows = read_csv(filename)

    added = 0
    updated = 0
    unchanged = 0
    errors = 0

    for line_number, row in enumerate(rows, start=2):

        try:

            name = row.get("name", "").strip()
            postcode = row.get("postcode", "").strip()
            region_name = row.get("region", "").strip()
            latitude = to_float(row.get("latitude", "").strip())
            longitude = to_float(row.get("longitude", "").strip())
            lga = row.get("lga", "").strip()

            if not name:
                raise ValueError("Missing locality name")

            if not postcode:
                raise ValueError("Missing postcode")

            region = None

            if region_name:
                region = db.session.execute(
                    select(Region).where(Region.name == region_name)
                ).scalar_one_or_none()

            locality = db.session.execute(
                select(Locality).where(
                    func.upper(Locality.name) == name.upper(),
                    Locality.postcode == postcode,
                )
            ).scalar_one_or_none()

            if locality is None:

                locality = Locality(
                    name=name,
                    postcode=postcode,
                    region=region,
                    latitude=latitude,
                    longitude=longitude,
                    lga=lga,
                )

                db.session.add(locality)
                added += 1

            else:

                changed = False

                if locality.name != name:
                    locality.name = name
                    changed = True

                if locality.region != region:
                    locality.region = region
                    changed = True

                if locality.latitude != latitude:
                    locality.latitude = latitude
                    changed = True

                if locality.longitude != longitude:
                    locality.longitude = longitude
                    changed = True

                if locality.lga != lga:
                    locality.lga = lga
                    changed = True

                if changed:
                    updated += 1
                else:
                    unchanged += 1

        except Exception as ex:

            print(f"  ERROR: {filename.name} line {line_number}: {ex}")
            errors += 1

    try:
        db.session.commit()
    except Exception as ex:
        db.session.rollback()
        print(f"\nDatabase commit failed: {ex}")
        return

    print_summary(
        "Localities",
        added,
        updated,
        unchanged,
        errors,
    )



def load_school_types() -> None:
    """
    Load school types from seed/school_types.csv.
    Insert them into the database if they don't already exist.
    Update them if they do exist and have changed.
    """

    print("Loading School Types...")

    filename = SEED_DIR / "school_types.csv"

    rows = read_csv(filename)

    added = 0
    updated = 0
    unchanged = 0
    errors = 0

    for line_number, row in enumerate(rows, start=2):

        try:

            code = row.get("code", "").strip()
            name = row.get("name", "").strip()
            description = row.get("description", "").strip()

            if not code:
                raise ValueError("Missing school type code")

            school_type = db.session.execute(
                select(SchoolType).filter_by(code=code)
            ).scalar_one_or_none()

            if school_type is None:

                school_type = SchoolType(
                    code=code,
                    name=name,
                    description=description,
                )

                db.session.add(school_type)
                added += 1

            else:

                changed = False

                #
                # Future school type fields go here.
                #

                if changed:
                    updated += 1
                else:
                    unchanged += 1

        except Exception as ex:

            print(f"  ERROR: {filename.name} line {line_number}: {ex}")
            errors += 1

    try:
        db.session.commit()
    except Exception as ex:
        db.session.rollback()
        print(f"\nDatabase commit failed: {ex}")
        return

    print_summary(
        "School Types",
        added,
        updated,
        unchanged,
        errors,
    )


def load_faculties() -> None:
    """
    Load faculties from seed/faculties.csv.
    Insert them into the database if they don't already exist.
    Update them if they do exist and have changed.
    """

    print("Loading Faculties...")

    filename = SEED_DIR / "faculties.csv"

    rows = read_csv(filename)

    added = 0
    updated = 0
    unchanged = 0
    errors = 0

    for line_number, row in enumerate(rows, start=2):

        try:

            code = row.get("code", "").strip()
            name = row.get("name", "").strip()
            faculty = row.get("faculty", "").strip()

            if not code:
                raise ValueError("Missing faculty code")

            faculty = db.session.execute(
                select(Faculty).filter_by(code=code)
            ).scalar_one_or_none()

            if faculty is None:

                faculty = Faculty(
                    code=code,
                    name=name,
                )

                db.session.add(faculty)
                added += 1

            else:

                changed = False

                #
                # Future faculty fields go here.
                #

                if changed:
                    updated += 1
                else:
                    unchanged += 1

        except Exception as ex:

            print(f"  ERROR: {filename.name} line {line_number}: {ex}")
            errors += 1

    try:
        db.session.commit()
    except Exception as ex:
        db.session.rollback()
        print(f"\nDatabase commit failed: {ex}")
        return

    print_summary(
        "Faculties",
        added,
        updated,
        unchanged,
        errors,
    )


def load_subjects() -> None:
    """
    Load subjects from seed/subjects.csv.
    Insert them into the database if they don't already exist.
    Update them if they do exist and have changed.
    """

    print("Loading Subjects...")

    filename = SEED_DIR / "subjects.csv"

    rows = read_csv(filename)

    added = 0
    updated = 0
    unchanged = 0
    errors = 0

    for line_number, row in enumerate(rows, start=2):

        try:

            code = row.get("code", "").strip()
            if not code:
                raise ValueError("Missing subject code")

            name = row.get("name", "").strip()
            if not name:
                raise ValueError("Missing subject name")

            faculty_code = row.get("faculty", "").strip()
            faculty = db.session.execute(
                select(Faculty).filter_by(code=faculty_code)
            ).scalar_one_or_none()

            if faculty is None:
                raise ValueError(
                    f"Unknown faculty code '{faculty_code}'"
                )

            active = row.get("active", "1").strip().lower() in (
                "1",
                "true",
                "yes",
                "y",
            )

            sort_order = row.get("sort_order", "0").strip()
            if sort_order == "":
                sort_order = 0
            elif sort_order.isdigit():
                sort_order = int(sort_order)
            else:
                raise ValueError("Invalid sort order")

            subject = db.session.execute(
                select(Subject).filter_by(code=code)
            ).scalar_one_or_none()

            if subject is None:

                subject = Subject(
                    code=code,
                    name=name,
                    faculty=faculty,
                    active=active,
                    sort_order=sort_order,
                )

                db.session.add(subject)
                added += 1

            else:

                changed = False

                if subject.name != name:
                    subject.name = name
                    changed = True

                if subject.faculty_id != faculty.id:
                    subject.faculty = faculty
                    changed = True

                if subject.active != active:
                    subject.active = active
                    changed = True

                if subject.sort_order != sort_order:
                    subject.sort_order = sort_order
                    changed = True

                if changed:
                    updated += 1
                else:
                    unchanged += 1

        except Exception as ex:

            print(f"  ERROR: {filename.name} line {line_number}: {ex}")
            errors += 1

    try:
        db.session.commit()
    except Exception as ex:
        db.session.rollback()
        print(f"\nDatabase commit failed: {ex}")
        return

    print_summary(
        "Subjects",
        added,
        updated,
        unchanged,
        errors,
    )

    print_subject_summary()


def load_schools() -> None:
    print("Loading Schools...")
    print_summary("Schools", 0, 0, 0, 0)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> int:

    app: Flask = create_app()

    with app.app_context():

        print_header()

        load_regions()
        load_localities()
        load_school_types()
        load_faculties()
        load_subjects()
        load_schools()

        print_footer()

    return 0


if __name__ == "__main__":
    sys.exit(main())
