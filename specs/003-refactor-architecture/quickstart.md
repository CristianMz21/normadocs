# NormaDocs Library Quickstart

After the architectural refactor, `normadocs` can be used directly as a pure Python library without depending on the CLI terminal environment.

## Installation

```bash
pip install normadocs
```

## Basic Conversion

```python
from pathlib import Path
from normadocs.converter import Converter, ConvertOptions
from normadocs.exceptions import NormaDocsError

def run_conversion():
    # 1. Setup options
    options = ConvertOptions(
        input_file=Path("my_thesis.md"),
        output_dir=Path("./export"),
        format="pdf",
        style="apa7estudiante"
    )

    # 2. Convert and handle errors gracefully
    try:
        converter = Converter(options)
        converter.convert_document()
        print("Success! Document generated.")
    except NormaDocsError as e:
        print(f"Failed to convert document: {e}")

if __name__ == "__main__":
    run_conversion()
```

## Configuring Logging

The core library uses standard Python `logging`. To see the progress output:

```python
import logging

logging.basicConfig(level=logging.INFO)
```
