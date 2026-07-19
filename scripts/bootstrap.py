"""
bootstrap.py

Completely rebuild the TeachWhere database.

SAFETY:
    Before running this script you MUST manually delete:

        instance/teachwhere.db
        migrations/

    This prevents accidental destruction of a working database.
"""

from pathlib import Path
import subprocess
import sys

from colorama import Fore, Style

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.utils.banner import title_banner


DATABASE = Path("instance/teachwhere.db")
MIGRATIONS = Path("migrations")


def run(command: str) -> None:
    """Run a shell command."""

    print(f"\n>>> {command}")

    result = subprocess.run(
        command,
        shell=True
    )

    if result.returncode != 0:
        print(f"\n{Fore.RED}Bootstrap failed.{Style.RESET_ALL}")
        sys.exit(result.returncode)


def main():

    title_banner("TeachWhere Database Bootstrap")

    # ---------------------------------------------------------
    # Safety checks
    # ---------------------------------------------------------

    if DATABASE.exists():

        print(
            f"\n{Fore.RED}ERROR:{Style.RESET_ALL} Database still exists.\n"
            "Delete it manually before running bootstrap."
        )

        return

    if MIGRATIONS.exists():

        print(
            f"\n{Fore.RED}ERROR:{Style.RESET_ALL} migrations folder still exists.\n"
            "Delete it manually before running bootstrap."
        )

        return

    # ---------------------------------------------------------
    # Flask-Migrate
    # ---------------------------------------------------------

    run("py -m flask db init")

    run('py -m flask db migrate -m "Initial database"')

    run("py -m flask db upgrade")

    # ---------------------------------------------------------
    # Populate database
    # ---------------------------------------------------------

    run("py scripts/build_localities.py")

    run("py scripts/seed.py")

    run("py scripts/import_nsw_schools.py")

    run("py scripts/merge_rural_incentive_info.py")

    print(f"\n{Fore.GREEN}Database bootstrap complete.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
