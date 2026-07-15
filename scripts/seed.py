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

from sqlalchemy import select

from app.models.geography import Region


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


# ---------------------------------------------------------------------
# Loader Functions
# ---------------------------------------------------------------------

def load_regions() -> None:
    """
    Load regions from seed/regions.csv.
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

            name = row["name"].strip()

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
    print("Loading Localities...")
    print_summary("Localities", 0, 0, 0, 0)


def load_school_types() -> None:
    print("Loading School Types...")
    print_summary("School Types", 0, 0, 0, 0)


def load_faculties() -> None:
    print("Loading Faculties...")
    print_summary("Faculties", 0, 0, 0, 0)


def load_subjects() -> None:
    print("Loading Subjects...")
    print_summary("Subjects", 0, 0, 0, 0)


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