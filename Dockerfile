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

# uv binary from a pinned upstream release
COPY --from=ghcr.io/astral-sh/uv:0.9.16 /uv /uvx /bin/

# Copy only what the locked install needs; keeps local artifacts out
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src

# Install the project and its runtime dependencies, pinned by uv.lock.
# Runs as a non-root user: the CLI writes its output into the CWD.
ENV UV_PYTHON_DOWNLOADS=never
RUN useradd --create-home --uid 1000 appuser \
    && uv sync --frozen --no-dev --python /usr/local/bin/python3 \
    && mkdir -p /app/ExportDocs \
    && chown -R appuser:appuser /app

ENV PATH="/app/.venv/bin:$PATH"
USER appuser

# Default command: Show help
CMD ["normadocs", "--help"]
