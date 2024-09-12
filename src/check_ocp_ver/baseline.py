"""Create the releses db to check against."""

from typing import List, Dict, Set

import requests
from bs4 import BeautifulSoup
from tinydb import TinyDB


def get_tables() -> List[str]:
    """Change this to select the HTML table to scrape"""
    return ["4stable_table", "4devpreview_table"]


def get_stable_releases() -> Set[str]:
    """Change this to select the stable versions."""
    return {"4.14", "4.16", "4.17"}


def get_preview_releases() -> Set[str]:
    """Change this to select the development versions."""
    return {"4.18"}


def filter_interested_releases(group_idx: int, row: List[str], table: str):
    """Change this to filter versions"""
    group: str = row[group_idx]
    if table == "4stable_table":
        if group in get_stable_releases():
            return True
    if table == "4devpreview_table":
        if group in get_preview_releases():
            return True
    return False


def to_dicts(header: List[str], rows: List[List[str]]) -> List[Dict[str, str]]:
    data: List[Dict[str, str]] = []
    for row in rows:
        entry = {}
        for i, key in enumerate(header):
            entry[key] = row[i]
        data.append(entry)
    return data


def filter_stable_and_accepted_releases(parsed_page) -> List[Dict[str, str]]:
    data: List[Dict[str, str]] = []
    for table in get_tables():
        t = parsed_page.find("table", {"id": table})
        header: List[str] = []
        rows: List[List[str]] = []
        group_idx: int = 0
        phase_idx: int = 0
        for i, row in enumerate(t.find_all("tr")):
            if i == 0:
                header = [el.text.strip() for el in row.find_all("th")]
                group_idx = header.index("Version Grouping")
                phase_idx = header.index("Phase")
            else:
                rows.append([el.text.strip() for el in row.find_all("td")])
        gen_rows = (r for r in rows if filter_interested_releases(group_idx, r, table))
        rows = [r for r in gen_rows if r[phase_idx] == "Accepted"]
        data = data + to_dicts(header, rows)
    return data


def save(data: List[Dict[str, str]]):
    db = TinyDB("stable_accepted_releases.json")
    for entry in data:
        db.insert(entry)


def main():
    r = requests.get("https://openshift-release.apps.ci.l2s4.p1.openshiftapps.com/")
    if r.status_code == 200:
        parsed_page = BeautifulSoup(r.text, features="html.parser")
        data = filter_stable_and_accepted_releases(parsed_page)
        save(data)
    else:
        print("status_code", r.status_code)


if __name__ == "__main__":
    main()
