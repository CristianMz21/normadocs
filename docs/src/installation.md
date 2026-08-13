# Installation

## Requirements

- **Python** 3.10 or higher
- **Pandoc** (required for conversion)

## Install Pandoc

```bash
# Debian/Ubuntu
sudo apt install pandoc

# macOS
brew install pandoc

# Windows
# Download from https://pandoc.org/installing.html
```

## Install NormaDocs

### From PyPI

```bash
pip install normadocs

# PDF generation plus strict APA PDF verification
pip install "normadocs[pdf,pdf-verifier]"
```

### From Source

```bash
git clone https://github.com/CristianMz21/normadocs.git
cd normadocs
pip install -e ".[dev]"
```

## Verify Installation

```bash
pandoc --version
normadocs --help
```

`normadocs --version` is not currently exposed by the CLI; use the installed
package metadata when an automation system needs the package version.
