# Use Python 3.12 as base image (no critical security issues)
FROM python:3.12-slim

# Update system packages and install uv tool
RUN apt-get update && apt-get upgrade -y && \
    pip install --no-cache-dir uv && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# Install only production dependencies using uv
RUN uv sync --frozen --no-dev

# Set environment variables with defaults
ENV CHECK_DB_DIR=/data
ENV CHECK_DB_FILE=stable_accepted_releases.json

# Create the data directory that will be used as mount point
RUN mkdir -p /data

# Set the Python path to include our source directory
ENV PYTHONPATH=/app/src/check_ocp_ver

# Change to the source directory where entrypoint.py is located
WORKDIR /app/src/check_ocp_ver

# Run the entrypoint script using uv
CMD ["uv", "run", "entrypoint.py"]
