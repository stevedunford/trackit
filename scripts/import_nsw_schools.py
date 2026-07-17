"""
Synchronise the School table with the NSW Public Schools Master Dataset.

The NSW Public Schools Master Dataset is the authoritative source for
school identity, contact details, enrolment, location and official
school attributes.

TRACKit extends this data with application-specific information such as
aliases, vacancy history and user data.
"""


from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

from sqlalchemy import func, inspect, select

# ---------------------------------------------------------------------
# Make project root importable
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.extensions import db
from app.models import Locality, School, SchoolType
from app.models.school import Remoteness


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

IMPORT_DIR = PROJECT_ROOT / "imports"

DEFAULT_FILE = IMPORT_DIR / "master_dataset.csv"

REQUIRED_COLUMNS = (
    "School_code",
    "School_name",
    "Town_suburb",
    "Level_of_schooling",
    "Latitude",
    "Longitude",
)

LEVEL_MAP = {
    "Infants School": "IS",
    "Primary School": "PS",
    "Secondary School": "HS",
    "Central/Community School": "CES",
    "School for Specific Purposes": "SSP",
    "Schools for Specific Purposes": "SSP",
    "Environmental Education Centre": "EEC",
    "Other School": "OTHER",
}

REMOTENESS_MAP = {
    "Major Cities of Australia": Remoteness.MAJOR_CITIES,
    "Inner Regional Australia": Remoteness.INNER_REGIONAL,
    "Outer Regional Australia": Remoteness.OUTER_REGIONAL,
    "Remote Australia": Remoteness.REMOTE,
    "Very Remote Australia": Remoteness.VERY_REMOTE,
}


def read_csv(filename: Path) -> list[dict]:
    """
    Read a CSV file and return a list of dictionaries.
    """

    with filename.open(
        newline="",
        encoding="utf-8-sig",
    ) as f:

        reader = csv.DictReader(f)

        return [
            {
                (key.strip() if key else ""):
                (value.strip() if value else "")
                for key, value in row.items()
            }
            for row in reader
        ]


def validate_columns(rows: list[dict]) -> bool:

    if not rows:
        print("CSV contains no data.")
        return False

    headers = rows[0].keys()

    missing = [
        col
        for col in REQUIRED_COLUMNS
        if col not in headers
    ]

    if missing:

        print("Missing columns:")

        for column in missing:
            print(f"    {column}")

        return False

    return True


def print_dataset_summary(rows: list[dict]):

    extracted = {
        row.get("Date_extracted", "")
        for row in rows
    }

    print("=" * 60)
    print("TRACKit NSW Schools Import")
    print("=" * 60)

    print(f"CSV File            : {DEFAULT_FILE.name}")
    print(f"Schools in dataset  : {len(rows)}")
    existing = db.session.scalar(
        select(func.count()).select_from(School)
    )
    print(f"Schools in database : {existing}")

    if len(extracted) == 1:
        print(f"Date Extracted      : {next(iter(extracted))}")
    else:
        print("Date Extracted      : Multiple values")

    print()


def normalise_name(text: str) -> str:
    """
    Normalise text for lookups.

    Removes leading/trailing whitespace, collapses multiple spaces
    and converts to uppercase.
    """

    return " ".join(text.strip().upper().split())


def parse_int(value: str) -> int | None:
    """
    Convert a CSV value to an integer.

    Returns None for blank values.
    """

    value = value.strip()

    if not value:
        return None

    return int(float(value))


def parse_float(value: str) -> float | None:
    """
    Convert a CSV value to a float.

    Returns None for blank values.
    """

    value = value.strip()

    if not value:
        return None

    return float(value)


def parse_bool(value: str) -> bool:
    """
    Convert Y/N values to True/False.
    """

    return value.strip().upper() == "Y"


def main():

    added = 0
    updated = 0
    unchanged = 0
    errors = 0

    print()

    app = create_app()

    with app.app_context():

        if not DEFAULT_FILE.exists():

            print(f"Cannot find {DEFAULT_FILE}")
            return 1

        rows = read_csv(DEFAULT_FILE)

        if not validate_columns(rows):
            return 1

        print_dataset_summary(rows)

        print("Loading reference data...")

        localities = {
            (
                normalise_name(locality.name),
                locality.postcode,
            ): locality
            for locality in db.session.scalars(
                select(Locality)
            )
        }

        school_types = {
            school.code: school
            for school in db.session.scalars(
                select(SchoolType)
            )
        }

        print(f"  Localities : {len(localities)}")
        print(f"  Types      : {len(school_types)}")
        print()

        print("Importing schools...")
        print()

        for line_number, row in enumerate(rows, start=2):

            try:

                school_code = parse_int(row["School_code"])

                locality = localities.get(
                    (
                        normalise_name(row["Town_suburb"]),
                        row["Postcode"],
                    )
                )

                if locality is None:
                    raise ValueError(
                        f"Unknown locality "
                        f"{row['Town_suburb']} "
                        f"({row['Postcode']})"
                    )

                code = LEVEL_MAP.get(row["Level_of_schooling"])
                if code is None:
                    raise ValueError(
                        f"Unknown school type "
                        f"{row['Level_of_schooling']}"
                    )
                
                school_type = school_types.get(code)

                if school_type is None:
                    raise ValueError(
                        f"SchoolType '{code}' not found"
                    )

                school = db.session.scalar(
                    select(School).where(
                        School.school_code == school_code
                    )
                )

                creating = school is None
                if creating:
                    school = School(
                        school_code=school_code,
                    )
                    db.session.add(school)

                state = inspect(school)
                
                if creating:
                    added += 1
                elif state.modified:
                    updated += 1
                else:
                    unchanged += 1

                #
                # Populate fields
                #

                school.locality = locality
                school.school_type = school_type

                school.name = row["School_name"]
                school.address = row["Street"]
                school.town_suburb = row["Town_suburb"]
                school.postcode = row["Postcode"]
                school.phone = row["Phone"]
                school.email = row["School_Email"]
                school.website = row["Website"]

                school.latitude = parse_float(row["Latitude"])
                school.longitude = parse_float(row["Longitude"])

                school.enrolment = parse_int(
                    row["latest_year_enrolment_FTE"]
                )

                school.foei = parse_int(
                    row["FOEI_Value"]
                )

                school.icsea = parse_int(
                    row["ICSEA_value"]
                )

                school.selective = (
                    row["Selective_school"] != "Not Selective"
                )

                school.connected_communities = (
                    "Connected Communities"
                    in row["Operational_directorate"]
                )

                school.remoteness = REMOTENESS_MAP.get(
                    row["ASGS_remoteness"]
                )

                school.last_updated = (
                    date.fromisoformat(row["Date_extracted"])
                    if row["Date_extracted"]
                    else None
                )

            except Exception as ex:

                print(
                    f"Line {line_number}: {ex}"
                )

                errors += 1

        db.session.commit()

        print()
        print("Import Summary")
        print("------------------------")
        print(f"Added      : {added}")
        print(f"Updated    : {updated}")
        print(f"Unchanged  : {unchanged}")
        print(f"Errors     : {errors}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
