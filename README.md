Openshift version checker
-------------------------

A script to check if new Openshift versions are available.

# Usage
- Create a baseline: a database contaning interested versions.
- Launch a script to check if new versions are available after the baseline creation time.

# Dependencies
- Install `uv`
  - `curl -LsSf https://astral.sh/uv/install.sh | sh`
- `uv sync` (installs dependencies from pyproject.toml)

# Create a baseline
- `uv run src/check_ocp_ver/baseline.py`

# Check for new versions
- `uv run src/check_ocp_ver/check.py`

# Local Development Setup

For local development with all dependencies including development tools:

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install all dependencies (including dev tools like black)
uv sync

# For production-only dependencies (without dev tools)
uv sync --no-dev

# Run with uv
uv run src/check_ocp_ver/baseline.py
uv run src/check_ocp_ver/check.py
```

# Container Usage

## Build the container:
```bash
docker build -t check-ocp-ver .
```

## Run the container with volume mounting:

**Basic usage (using current directory as shared volume):**
```bash
# For Docker (Linux/Windows)
docker run -v $(pwd):/data check-ocp-ver

# For macOS - recommended setup with Colima (lightweight Docker alternative)
# Install Colima: brew install colima
# Start Colima: colima start
docker run -v $(pwd):/data check-ocp-ver
```

**With custom environment variables:**
```bash
docker run \
  -v $(pwd):/data \
  -e CHECK_DB_DIR=/data \
  -e CHECK_DB_FILE=my_custom_releases.json \
  check-ocp-ver
```

**Using a specific directory as shared volume:**
```bash
docker run -v /path/to/your/data:/data check-ocp-ver
```

## macOS Setup with Colima

For macOS users, we recommend using **Colima** instead of Docker Desktop for better performance and resource management:

```bash
# Install Colima (one-time setup)
brew install colima docker

# Start Colima (creates a lightweight VM)
colima start

# Now you can use docker commands normally
docker build -t check-ocp-ver .
docker run -v $(pwd):/data check-ocp-ver

# Stop Colima when done (optional)
colima stop
```

**Why Colima on macOS?**
- ✅ Lightweight and fast
- ✅ Free and open source  
- ✅ Better volume permission handling
- ✅ Lower resource usage than Docker Desktop
- ✅ No licensing concerns

## How it Works

1. **First run**: If no database file exists in the shared volume, the container will run `baseline.py` to create the initial JSON database by scraping the OpenShift releases page.

2. **Subsequent runs**: If the database file exists, the container will run `check.py` to compare current releases against the saved baseline and report any new releases.

3. **Shared volume**: The `/data` directory in the container is mapped to your host directory, allowing the database file to persist between container runs.

The container uses environment variables:
- `CHECK_DB_DIR` (default: `/data`) - Directory path in the container where the database file is stored
- `CHECK_DB_FILE` (default: `stable_accepted_releases.json`) - Name of the database file
