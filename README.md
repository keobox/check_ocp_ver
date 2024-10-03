Openshift version checker
-------------------------

A script to check if new Openshift versions are available.

# Usage
- Create a baseline: a database contaning interested versions.
- Launch a script to check if new versions are available after the baseline creation time.

# Dependencies
- Install `uv`
  - `curl -LsSf https://astral.sh/uv/install.sh | sh`
- `uv venv`
- `uv pip install -r requirements.txt`

# Create a baseline
- `uv run src/check_ocp_ver/baseline.py`

# Check for new versions
- `uv run src/check_ocp_ver/check.py`
