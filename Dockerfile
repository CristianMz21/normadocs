FROM python:3.12-slim-bookworm

ARG VERSION=0.2.0
ARG BUILD_DATE=$(date -u +'%Y-%m-%d')

LABEL maintainer="Cristian Muñoz <cristianmz21@users.noreply.github.com>"
LABEL description="Markdown to academic DOCX/PDF converter (APA 7th, ICONTEC, IEEE)"
LABEL version="${VERSION}"
LABEL build-date="${BUILD_DATE}"

# Install System dependencies
# Pandoc (Core), LibreOffice (PDF), and WeasyPrint deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    default-jre-headless \
    libcairo2 \
    libffi-dev \
    libjpeg62-turbo \
    libopenjp2-7 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libreoffice-java-common \
    libreoffice-writer \
    make \
    pandoc \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy hashed lock and project metadata; keep uv.lock in repo for local dev only
COPY requirements-ci.txt pyproject.toml README.md LICENSE ./
COPY src ./src

# Install runtime dependencies with hash verification (CWE-829/CWE-506).
# Uses plain pip with --require-hashes so Sonar S8541/S8544 is clean.
# Project code is executed via PYTHONPATH + wrapper script to avoid
# a second install without hashes.
ENV PYTHONPATH=/app/src
RUN pip install --no-build --only-binary :all: --require-hashes -r requirements-ci.txt \
    && useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/ExportDocs \
    && chown -R appuser:appuser /app \
    && printf '#!/bin/sh\nexec python -m normadocs "$@"\n' > /usr/local/bin/normadocs \
    && chmod +x /usr/local/bin/normadocs

USER appuser

# Default command: Show help
CMD ["normadocs", "--help"]
