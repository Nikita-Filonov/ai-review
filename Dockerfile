ARG PYTHON_VERSION=3.12-slim-bullseye
FROM python:${PYTHON_VERSION}

WORKDIR /app

RUN apt-get update && \
    apt-get install -y bash ca-certificates curl git libexpat1 openssh-client && \
    rm -rf /var/lib/apt/lists/*

ARG AI_REVIEW_VERSION
RUN pip install --no-cache-dir xai-review==${AI_REVIEW_VERSION}