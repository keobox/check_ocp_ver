"""Check current page against last saved page."""

import requests
from bs4 import BeautifulSoup
from tinydb import TinyDB, where
from baseline import filter_stable_and_accepted_releases


def check(current, baseline):
    """Change this to check different versions"""
    check_ver("4.14", current, baseline)
    check_ver("4.16", current, baseline)
    check_ver("4.17", current, baseline)


def sort_by_latest_version(saved_versions):
    for entry in saved_versions:
        ver = [v for v in entry["Name"].split(".")]
        if "rc" or "ec" in ver[2]:
            minor = ver[2].split("-")[0]
            ver[2] = minor
        ver = tuple([int(v) for v in ver])
        entry["ver"] = ver
    saved_versions.sort(key=lambda entry: entry["ver"], reverse=True)


def check_ver(version, current, baseline):
    current_group = [r for r in current if r["Version Grouping"] == version]
    saved_group = baseline.search(where("Version Grouping") == version)
    sort_by_latest_version(saved_group)
    current_ver = current_group[0]["Name"]
    saved_ver = saved_group[0]["Name"]
    if current_ver != saved_ver:
        print("New version:", current_ver)
        baseline.insert(current_group[0])
        print("saved!")
    else:
        print("Current version:", current_ver, "Saved version:", saved_ver)


def load():
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
