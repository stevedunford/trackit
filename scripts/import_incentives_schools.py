"""
extract_rural_incentives.py

Extract NSW Rural Incentive School information from the
downloaded Department of Education HTML page.

Creates:

    imports/rural_incentive_schools.csv
"""

from pathlib import Path
import csv

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent

html_file = ROOT / "imports" / "rural_incentive_schools.html"
csv_file = ROOT / "imports" / "rural_incentive_schools.csv"

with open(html_file, encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

rows = []

for tr in soup.select("tbody tr"):

    cells = tr.find_all("td")

    if len(cells) != 4:
        continue

    #
    # School name
    #

    school_link = cells[0].find("a")

    school_name = school_link.get_text(strip=True)

    school_code = cells[1].get_text(strip=True)

    #
    # Points / Connected Communities
    #

    points_text = cells[2].get_text(strip=True)

    is_cc = "(CC)" in points_text

    points = points_text.replace("(CC)", "").strip()

    #
    # Community page
    #

    area_link = cells[3].find("a")

    html_link = area_link["href"] if area_link else ""
    if html_link[0] == "/":
        html_link = "https://education.nsw.gov.au" + html_link

    rows.append({
        "name": school_name,
        "school_code": school_code,
        "points": int(points),
        "is_cc": is_cc,
        "html_link": html_link,
    })
    

with open(csv_file, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "name",
            "school_code",
            "points",
            "is_cc",
            "html_link",
        ],
    )

    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} schools")
print(csv_file)