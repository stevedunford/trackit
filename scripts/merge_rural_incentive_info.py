"""
enrich_rural_incentives.py

Updates NSW schools with Rural & Remote incentive information.

Input:
    imports/rural_incentive_schools.csv
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app
from app.extensions import db
from app.models.school import School


CSV_FILE = ROOT / "imports" / "rural_incentive_schools.csv"

app = create_app()

with app.app_context():

    updated = 0
    unmatched = 0

    with open(CSV_FILE, newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            school = School.query.filter_by(
                school_code=int(row["school_code"])
            ).first()

            if school is None:

                unmatched += 1

                print(
                    f"School code {row['school_code']} "
                    f"({row['name']}) not found."
                )

                continue

            #
            # Enrichment
            #

            school.transfer_points = int(row["points"])

            school.is_connected_community = (
                row["is_cc"].strip().lower()
                in ("true", "1", "yes", "y")
            )

            school.community_information_url = row["html_link"]

            updated += 1

    db.session.commit()

    print()
    print("---------------------------------------")
    print(f"Schools updated : {updated}")
    print(f"Not matched     : {unmatched}")
    print("---------------------------------------")