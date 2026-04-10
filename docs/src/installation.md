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

# With PDF support
pip install normadocs[pdf]
```

### From Source

```bash
git clone https://github.com/CristianMz21/normadocs.git
cd normadocs
pip install -e ".[dev]"
```

## Verify Installation

```bash
normadocs --version
normadocs --help
```
