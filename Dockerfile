FROM python:3.12-slim-bookworm

# Install Pandoc (System dependency) and LibreOffice for PDF conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    libreoffice-writer \
    libreoffice-java-common \
    default-jre-headless \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Run the script using uv
# We use 'uv run' which automatically sets up a virtualenv and installs dependencies
CMD ["uv", "run", "convert_to_apa.py"]
