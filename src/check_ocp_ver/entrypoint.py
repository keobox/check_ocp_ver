"""Entrypoint of the check Openshift version 'service'"""

import os

import baseline
import check


def main():
    """If a version database file does not exists create one, otherwise just query the
    Openshift release web page and compare against the past saved versions."""
    db_dir = os.environ.get("CHECK_DB_DIR", ".")
    db_file = os.environ.get("CHECK_DB_FILE", "stable_accepted_releases.json")
    if os.path.exists(os.path.join(db_dir, db_file)):
        check.main()
    else:
        baseline.main()


if __name__ == "__main__":
    main()
