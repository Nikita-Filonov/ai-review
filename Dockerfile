# ==============================
# AI Review Dockerfile
# ==============================

# Use a slim Python base image (smaller size, faster builds)
ARG PYTHON_VERSION=3.11-slim-bullseye
FROM python:${PYTHON_VERSION}

# Install system dependencies required for building some Python packages
# - build-essential: compilers and basic tools
# - git: may be needed if dependencies are fetched from Git repositories
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy all project files into the container
COPY . .

# Install the project as a Python package (from pyproject.toml)
RUN pip install --no-cache-dir .

# Set the default entrypoint to the CLI command
ENTRYPOINT ["ai-review"]