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
    return {"4.16", "4.18", "4.19"}


def get_preview_releases() -> Set[str]:
    """Change this to select the development versions."""
    return {"4.20"}


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


def filter_latest_stable_and_accepted_releases(parsed_page) -> List[Dict[str, str]]:
    data: List[Dict[str, str]] = []
    for table in get_tables():
        t = parsed_page.find("table", {"id": table})
        header: List[str] = []
        rows: List[List[str]] = []
        group_idx: int = 0
        prev_ver: str = ""
        for i, row in enumerate(t.find_all("tr")):
            if i == 0:
                header = [el.text.strip() for el in row.find_all("th")]
                group_idx = header.index("Version Grouping")
            else:
                current_ver_str: str = row.find_all("td")[0].text.strip()
                current_ver_str_list: List = current_ver_str.split(".")[:2]
                current_ver: str = ".".join(current_ver_str_list)
                version_fields: List = [el.text.strip() for el in row.find_all("td")]
                accepted: bool = "Accepted" == version_fields[1]
                if accepted and current_ver != prev_ver:
                    rows.append(version_fields)
                    prev_ver = current_ver
        rows = [r for r in rows if filter_interested_releases(group_idx, r, table)]
        data = data + to_dicts(header, rows)
    return data


def save(data: List[Dict[str, str]]):
    db = TinyDB("stable_accepted_releases.json")
    for entry in data:
        item = {"Name": entry["Name"], "Version Grouping": entry["Version Grouping"]}
        db.insert(item)


def main():
    r = requests.get("https://openshift-release.apps.ci.l2s4.p1.openshiftapps.com/")
    if r.status_code == 200:
        parsed_page = BeautifulSoup(r.text, features="html.parser")
        data = filter_latest_stable_and_accepted_releases(parsed_page)
        save(data)
    else:
        print("status_code", r.status_code)


if __name__ == "__main__":
    main()
