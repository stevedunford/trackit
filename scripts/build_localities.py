"""
build_localities.py

Generate seed/localities.csv from the NSW master dataset.
"""

from pathlib import Path
import csv
import sys

from colorama import Fore, Style

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.utils.banner import title_banner


IMPORT_DIR = PROJECT_ROOT / "imports"
SEED_DIR = PROJECT_ROOT / "seed"

MASTER_DATASET = IMPORT_DIR / "NSW_GOVT_SCHOOL_LIST.csv"
LOCALITIES_CSV = SEED_DIR / "localities.csv"
BACKUP_CSV = SEED_DIR / "localities.csv.bak"


def print_header():

    title_banner("Trackit Localities CSVBuilder")
    print(f"Input  : {MASTER_DATASET.name}")
    print(f"Output : {LOCALITIES_CSV.name}")
    print()


def read_master_dataset():

    with MASTER_DATASET.open(
        newline="",
        encoding="utf-8-sig",
    ) as csvfile:

        return list(csv.DictReader(csvfile))


def extract_localities(rows, existing_regions):

    """
    Extract unique localities from the NSW master dataset.

    Returns a dictionary keyed by:
        (name, postcode)
    """

    localities = {}

    for row in rows:

        # title case all names, except for names starting
        # with "MC" (e.g. McDonald, McKenzie)
        # note: not handling names starting with "Mac" (e.g. MacDonald)
        # because none currently exist in the dataset
        name = row.get("Town_suburb", "").strip().title()
        if name.startswith("Mc") and len(name) > 2:
            name = name[0:2] + name[2].upper() + name[3:]

        postcode = row.get("Postcode", "").strip()

        if not name:
            continue

        lookup_key = (name.upper(), postcode)

        localities[lookup_key] = {
            "name": name,
            "postcode": postcode,
            "region": existing_regions.get(lookup_key, ""),
            "latitude": row.get("Latitude", "").strip(),
            "longitude": row.get("Longitude", "").strip(),
            "lga": row.get("LGA", "").strip(),
        }

    return dict(sorted(localities.items()))


def load_existing_regions():
    """
    Load any existing locality region assignments.

    Returns:
        dict[(name, postcode)] -> region
    """

    regions = {}

    if not LOCALITIES_CSV.exists():
        return regions

    with LOCALITIES_CSV.open(
        newline="",
        encoding="utf-8-sig",
    ) as csvfile:

        reader = csv.DictReader(csvfile)

        for row in reader:

            name = row.get("name", "").strip().upper()
            postcode = row.get("postcode", "").strip()
            region = row.get("region", "").strip()

            if name:

                regions[(name, postcode)] = region

    return regions


def backup_existing_csv():

    """
    Backup the existing localities.csv file.
    """

    if not LOCALITIES_CSV.exists():
        return

    if BACKUP_CSV.exists():
        BACKUP_CSV.unlink()

    LOCALITIES_CSV.rename(BACKUP_CSV)


def write_localities_csv(localities):

    with LOCALITIES_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "name",
            "postcode",
            "region",
            "latitude",
            "longitude",
            "lga",
        ])

        for locality in localities.values():

            writer.writerow([
                locality["name"],
                locality["postcode"],
                locality["region"],
                locality["latitude"],
                locality["longitude"],
                locality["lga"],
            ])


def main():

    print_header()

    rows = read_master_dataset()

    existing_regions = load_existing_regions()

    localities = extract_localities(
        rows,
        existing_regions,
    )

    backup_existing_csv()

    write_localities_csv(localities)

    existing_regions = sum(
        1
        for locality in localities.values()
        if locality["region"]
    )

    missing_regions = len(localities) - existing_regions

    print()
    print(f"{Fore.GREEN}Schools processed{Style.RESET_ALL}     : {len(rows)}")
    print(f"{Fore.GREEN}Unique localities{Style.RESET_ALL}     : {len(localities)}")
    print(f"{Fore.GREEN}Existing regions kept{Style.RESET_ALL} : {existing_regions}")
    if missing_regions:
        print(f"{Fore.YELLOW}Missing regions{Style.RESET_ALL}       : {missing_regions}")

    print()

    if BACKUP_CSV.exists():
        print(f"Backup written         : {BACKUP_CSV.name}")

    print(f"CSV written            : {LOCALITIES_CSV.name}")

    print()
    if missing_regions:
        print(f"{Fore.YELLOW}WARNING:{Style.RESET_ALL} "
              f"{missing_regions} localities are missing region")
        print(f" assignments. Please review {Fore.BLUE}{LOCALITIES_CSV}{Style.RESET_ALL} and update.")
    print()

    print("Done.")


if __name__ == "__main__":
    main()
