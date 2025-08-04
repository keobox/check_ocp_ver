"""Check current page against last saved page."""

from typing import Dict, List, Union

import requests
from bs4 import BeautifulSoup
from tinydb import Query, TinyDB, where
from baseline import filter_latest_stable_and_accepted_releases


def check(
    current_parsed_page: List[Dict[str, str]], baseline: TinyDB
) -> List[Dict[str, Union[str, bool]]]:
    """Change this to check different versions"""
    response: List[Dict[str, Union[str, bool]]] = []
    response.append(check_ver("4.16", current_parsed_page, baseline))
    response.append(check_ver("4.18", current_parsed_page, baseline))
    response.append(check_ver("4.19", current_parsed_page, baseline))
    response.append(check_ver("4.20", current_parsed_page, baseline))
    return response


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


def check_ver(
    version: str, current_page: List[Dict[str, str]], baseline: TinyDB
) -> Dict[str, Union[str, bool]]:
    current_group = [r for r in current_page if r["Version Grouping"] == version]
    saved_group = baseline.search(where("Version Grouping") == version)
    response: Dict[str, Union[str, bool]] = {}
    if not current_group:
        response["current_version"] = version
        response["saved_version"] = version
        response["status"] = "Not found in current page"
        response["changed"] = False
    elif not saved_group:
        new_current_ver: str = current_group[0]["Name"]
        response["current_version"] = version
        response["saved_version"] = new_current_ver
        response["status"] = "Version of a new group saved"
        response["changed"] = False
        save_and_acknowledge_version(new_current_ver, current_group, baseline)
    else:
        current_ver: str = current_group[0]["Name"]
        saved_ver: str = saved_group[0]["Name"]
        response["current_version"] = current_ver
        response["saved_version"] = saved_ver
        response["status"] = "ok"
        response["changed"] = False
        if current_ver != saved_ver:
            update_and_acknowledge_version(current_ver, saved_ver, baseline)
            response["changed"] = False
    return response


def load() -> TinyDB:
    return TinyDB("stable_accepted_releases.json")


def main():
    r = requests.get("https://openshift-release.apps.ci.l2s4.p1.openshiftapps.com/")
    if r.status_code == 200:
        parsed_page = BeautifulSoup(r.text, features="html.parser")
        data = filter_latest_stable_and_accepted_releases(parsed_page)
        db = load()
        print(check(data, db))
    else:
        print("status_code", r.status_code)


if __name__ == "__main__":
    main()
