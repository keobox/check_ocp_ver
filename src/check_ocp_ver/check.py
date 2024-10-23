"""Check current page against last saved page."""

from typing import Dict, List, Tuple

import requests
from bs4 import BeautifulSoup
from tinydb import TinyDB, where
from tinydb.table import Document
from baseline import filter_stable_and_accepted_releases


def check(current_parsed_page: List[Dict[str, str]], baseline: TinyDB):
    """Change this to check different versions"""
    check_ver("4.14", current_parsed_page, baseline)
    check_ver("4.16", current_parsed_page, baseline)
    check_ver("4.18", current_parsed_page, baseline)


def sort_by_latest_version(saved_versions: List[Document]):
    for entry in saved_versions:
        ver_s: List[str] = [v for v in entry["Name"].split(".")]
        if "ec" in ver_s[2]:
            ver_s[2] = "0"
        elif "rc" in ver_s[2]:
            ver_s[2] = "1"
        else:
            ver_s = [ver_s[0], ver_s[1], "2", ver_s[2]]
        ver: Tuple[int, ...] = tuple([int(v) for v in ver_s])
        entry["ver"] = ver
    saved_versions.sort(key=lambda entry: entry["ver"], reverse=True)


def check_ver(version: str, current_page: List[Dict[str, str]], baseline: TinyDB):
    current_group = [r for r in current_page if r["Version Grouping"] == version]
    saved_group = baseline.search(where("Version Grouping") == version)
    sort_by_latest_version(saved_group)
    if not current_group:
        print("version", version)
        print("Not found")
    else:
        current_ver: str = current_group[0]["Name"]
        saved_ver: str = saved_group[0]["Name"]
        if current_ver != saved_ver:
            print("New version:", current_ver)
            baseline.insert(current_group[0])
            print("saved!")
        else:
            print("Current version:", current_ver, "Saved version:", saved_ver)


def load() -> TinyDB:
    return TinyDB("stable_accepted_releases.json")


def main():
    r = requests.get("https://openshift-release.apps.ci.l2s4.p1.openshiftapps.com/")
    if r.status_code == 200:
        parsed_page = BeautifulSoup(r.text, features="html.parser")
        data = filter_stable_and_accepted_releases(parsed_page)
        db = load()
        check(data, db)
    else:
        print("status_code", r.status_code)


if __name__ == "__main__":
    main()
