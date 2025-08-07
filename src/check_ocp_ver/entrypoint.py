"""Entrypoint of the check Openshift version 'service'"""

import os

import baseline
import check


def main():
    """If a version database file does not exists create one, otherwise just query the
    Openshift release web page and compare against the past saved versions."""
    db_dir = os.environ.get("CHECK_DB_DIR", ".")
    db_file_name = os.environ.get("CHECK_DB_FILE", "stable_accepted_releases.json")
    db_file = os.path.join(db_dir, db_file_name)
    if os.path.exists(db_file):
        check.main(db_file)
    else:
        baseline.main(db_file)


if __name__ == "__main__":
    main()
