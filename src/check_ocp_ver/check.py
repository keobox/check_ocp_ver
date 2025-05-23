"""Check current page against last saved page."""

from typing import Dict, List, Tuple

import requests
from bs4 import BeautifulSoup
from tinydb import Query, TinyDB, where
from tinydb.table import Document
from baseline import filter_latest_stable_and_accepted_releases


def check(current_parsed_page: List[Dict[str, str]], baseline: TinyDB):
    """Change this to check different versions"""
    check_ver("4.16", current_parsed_page, baseline)
    check_ver("4.18", current_parsed_page, baseline)
    check_ver("4.19", current_parsed_page, baseline)
    check_ver("4.20", current_parsed_page, baseline)


def save_and_acknowledge_version(
    current_ver: str, current_group: List[Dict[str, str]], baseline: TinyDB
):
    print("New version:", current_ver)
    baseline.insert(current_group[0])
    print("saved!")


def update_and_acknowledge_version(current_ver: str, prev_ver: str, baseline: TinyDB):
    ver = Query()
    print("New version:", current_ver)
    baseline.update({"Name": current_ver}, ver.Name == prev_ver)
    print("updated!")


def check_ver(version: str, current_page: List[Dict[str, str]], baseline: TinyDB):
    current_group = [r for r in current_page if r["Version Grouping"] == version]
    saved_group = baseline.search(where("Version Grouping") == version)
    if not current_group:
        print("version", version)
        print("Not found in current page")
    elif not saved_group:
        print("version", version)
        print("Not saved")
        new_current_ver: str = current_group[0]["Name"]
        save_and_acknowledge_version(new_current_ver, current_group, baseline)
    else:
        current_ver: str = current_group[0]["Name"]
        saved_ver: str = saved_group[0]["Name"]
        if current_ver != saved_ver:
            update_and_acknowledge_version(current_ver, saved_ver, baseline)
        else:
            print("Current version:", current_ver, "Saved version:", saved_ver)


def load() -> TinyDB:
    return TinyDB("stable_accepted_releases.json")


def main():
    r = requests.get("https://openshift-release.apps.ci.l2s4.p1.openshiftapps.com/")
    if r.status_code == 200:
        parsed_page = BeautifulSoup(r.text, features="html.parser")
        data = filter_latest_stable_and_accepted_releases(parsed_page)
        db = load()
        check(data, db)
    else:
        print("status_code", r.status_code)


if __name__ == "__main__":
    main()
