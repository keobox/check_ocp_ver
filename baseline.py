"""Create the releses db to check against."""

import requests
from bs4 import BeautifulSoup
from tinydb import TinyDB


def get_table():
    """Change this to select the HTML table to scrape"""
    return "4stable_table"


def filter_interested_releases(group_idx, row):
    """Change this to filter versions"""
    group = row[group_idx]
    if group == "4.16" or group == "4.14":
        return True
    return False


def to_dicts(header, rows):
    data = []
    for row in rows:
        entry = {}
        for i, key in enumerate(header):
            entry[key] = row[i]
        data.append(entry)
    return data


def filter_stable_and_accepted_releases(s):
    t = s.find("table", {"id": get_table()})
    header = []
    rows = []
    group_idx = 0
    phase_idx = 0
    for i, row in enumerate(t.find_all("tr")):
        if i == 0:
            header = [el.text.strip() for el in row.find_all("th")]
            group_idx = header.index("Version Grouping")
            phase_idx = header.index("Phase")
        else:
            rows.append([el.text.strip() for el in row.find_all("td")])
    rows = (r for r in rows if filter_interested_releases(group_idx, r))
    rows = [r for r in rows if r[phase_idx] == "Accepted"]
    data = to_dicts(header, rows)
    return data


def save(data):
    db = TinyDB("stable_accepted_releases.json")
    for entry in data:
        db.insert(entry)


def main():
    r = requests.get("https://openshift-release.apps.ci.l2s4.p1.openshiftapps.com/")
    if r.status_code == 200:
        parsed = BeautifulSoup(r.text, features="html.parser")
        data = filter_stable_and_accepted_releases(parsed)
        save(data)
    else:
        print("status_code", r.status_code)


if __name__ == "__main__":
    main()
