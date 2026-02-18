FROM python:3.12-slim-bookworm

# Install System dependencies
# Pandoc (Core), LibreOffice (PDF), and WeasyPrint deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    libreoffice-writer \
    libreoffice-java-common \
    default-jre-headless \
    curl \
    ca-certificates \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libjpeg62-turbo \
    libopenjp2-7 \
    libffi-dev \
    shared-mime-info \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install the package
# This installs dependencies from pyproject.toml and creates the 'apa-format' command
RUN pip install --no-cache-dir .

# Default command: Show help
CMD ["normadocs", "--help"]
